
"""Conservative loop-invariant code motion for simple TAC."""

import re

from ..cfg import build_cfg

_LABEL = re.compile(r"^\s*([A-Za-z_]\w*):\s*$")
_ASSIGNMENT = re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.*?)\s*$")
_BINARY = re.compile(
    r"^([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*"
    r"(<<|>>|[+\-*/%])\s*"
    r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)$"
)
_VARIABLE = re.compile(r"^[A-Za-z_]\w*$")
_CONDITIONAL = re.compile(r"^\s*(if|ifFalse)\b")


def _assigned(line: str) -> str | None:
    match = _ASSIGNMENT.match(line)
    return match.group(1) if match else None


def _successors(cfg: dict, block_id: str) -> set[str]:
    return set(cfg["successors"].get(block_id, []))


def _compute_dominators(cfg: dict) -> dict[str, set[str]]:
    blocks = cfg["blocks"]
    if not blocks:
        return {}

    ids = [block["id"] for block in blocks]
    entry = ids[0]
    predecessors = cfg["predecessors"]

    dominators = {
        block_id: ({block_id} if block_id == entry else set(ids))
        for block_id in ids
    }

    changed = True
    while changed:
        changed = False

        for block_id in ids:
            if block_id == entry:
                continue

            preds = predecessors.get(block_id, [])
            if preds:
                common = set.intersection(
                    *(dominators[pred] for pred in preds)
                )
            else:
                common = set()

            updated = {block_id} | common
            if updated != dominators[block_id]:
                dominators[block_id] = updated
                changed = True

    return dominators



def _natural_loop(
    cfg: dict,
    header: str,
    tail: str,
) -> set[str]:
    """Find loop blocks for a back edge whose header dominates its tail."""
    # A self-loop needs only its header block.
    if tail == header:
        return {header}

    predecessors = cfg["predecessors"]
    loop = {header, tail}
    stack = [tail]

    while stack:
        current = stack.pop()

        for predecessor in predecessors.get(current, []):
            if predecessor == header:
                continue

            if predecessor not in loop:
                loop.add(predecessor)
                stack.append(predecessor)

    return loop


def _find_loops(cfg: dict) -> list[tuple[str, set[str]]]:
    dominators = _compute_dominators(cfg)
    loops = []

    for edge in cfg["edges"]:
        source = edge["from"]
        target = edge["to"]

        if target in dominators.get(source, set()):
            loop_blocks = _natural_loop(cfg, target, source)
            loops.append((target, loop_blocks))

    return loops


def _has_unsafe_entry(
    code: list[str],
    header_block: dict,
    loop_blocks: set[str],
    cfg: dict,
) -> bool:
    """Reject loops with entry paths that make hoisting unsafe."""
    header_start = header_block["start"]

    # A conditional before the loop can skip its body. Hoisting before
    # such a branch could execute an instruction that was previously skipped.
    for line in code[:header_start]:
        if _CONDITIONAL.match(line):
            return True

    # Reject loops with multiple external entry edges.
    blocks = {block["id"]: block for block in cfg["blocks"]}
    entries = 0

    for block_id in loop_blocks:
        for predecessor in cfg["predecessors"].get(block_id, []):
            if predecessor not in loop_blocks:
                entries += 1

    if entries > 1:
        return True

    # A loop header must be a recognizable label.
    instructions = header_block["instructions"]
    return not instructions or not _LABEL.match(instructions[0])

def analyze_licm_safety(code: list[str]) -> list[dict]:
    """Explain why simple loop-invariant assignments are safe or withheld."""
    report = []

    try:
        cfg = build_cfg(code)
    except (ValueError, KeyError):
        return [{
            "instruction": "",
            "decision": "withheld",
            "reason": "Could not build a valid control-flow graph."
        }]

    blocks = {block["id"]: block for block in cfg["blocks"]}
    loops = _find_loops(cfg)
    loops.sort(key=lambda item: len(item[1]))

    for header_id, loop_blocks in loops:
        header = blocks[header_id]

        if _has_unsafe_entry(code, header, loop_blocks, cfg):
            report.append({
                "instruction": header["instructions"][0]
                    if header["instructions"] else header_id,
                "decision": "withheld",
                "reason": "Loop entry or control flow makes hoisting unsafe."
            })
            continue

        external_preds = [
            predecessor
            for predecessor in cfg["predecessors"].get(header_id, [])
            if predecessor not in loop_blocks
        ]

        loop_instructions = [
            line
            for block_id in loop_blocks
            for line in blocks[block_id]["instructions"]
            if not _LABEL.match(line)
        ]

        for line in loop_instructions:
            assignment = _ASSIGNMENT.match(line)
            if not assignment:
                continue

            target, expression = assignment.groups()
            binary = _BINARY.fullmatch(expression)

            if not binary:
                continue

            left, operator, right = binary.groups()
            operands = {
                operand
                for operand in (left, right)
                if _VARIABLE.fullmatch(operand)
            }

            reason = None

            if not operands:
                reason = "Expression has no variable operands to justify LICM."
            elif target in operands:
                reason = "The assignment depends on its own target."
            elif operator in {"/", "%"}:
                reason = "Division and modulo are withheld to avoid trapping."
            elif any(
                _assigned(instruction) in operands
                for instruction in loop_instructions
            ):
                reason = "An operand is modified inside the loop."
            elif sum(
                _assigned(instruction) == target
                for instruction in loop_instructions
            ) != 1:
                reason = "The target has multiple assignments inside the loop."
            else:
                block = next(
                    blocks[block_id]
                    for block_id in loop_blocks
                    if line in blocks[block_id]["instructions"]
                )
                position = block["instructions"].index(line)

                if any(
                    _CONDITIONAL.match(instruction)
                    for instruction in block["instructions"][:position]
                ):
                    reason = (
                        "Hoisting could execute a conditionally skipped assignment."
                    )
                elif not external_preds:
                    reason = (
                        "The loop header has no external predecessor, "
                        "so the optimizer will not hoist this expression."
                    )

            report.append({
                "instruction": line,
                "decision": "withheld" if reason else "safe",
                "reason": reason or (
                    "Operands remain unchanged, the target is assigned once, "
                    "and the expression passes the conservative LICM checks."
                )
            })

    return report

def move_loop_invariants(code: list[str]) -> list[str]:
    """Hoist simple invariant assignments only when conservative checks pass."""
    result = list(code)

    if not result:
        return result

    try:
        cfg = build_cfg(result)
    except (ValueError, KeyError):
        return result

    blocks = cfg["blocks"]
    block_by_id = {block["id"]: block for block in blocks}
    loops = _find_loops(cfg)

    # Process innermost/smallest loops first.
    loops.sort(key=lambda item: len(item[1]))

    for header_id, loop_blocks in loops:
        header = block_by_id[header_id]

        if _has_unsafe_entry(result, header, loop_blocks, cfg):
            continue

        header_start = header["start"]
        header_end = header["end"]

        # Keep this implementation deliberately limited to a loop whose
        # body is a single basic block after the header label.
        
        # Collect instructions from loop blocks, including the header block.
        loop_instructions = []

        for block_id in loop_blocks:
            block = block_by_id[block_id]

            for line in block["instructions"]:
                if _LABEL.match(line):
                    continue
                loop_instructions.append(line)

        candidates = []

        for line in loop_instructions:
            assignment = _ASSIGNMENT.match(line)
            if not assignment:
                continue

            target, expression = assignment.groups()
            binary = _BINARY.fullmatch(expression)

            if not binary:
                continue

            left, operator, right = binary.groups()
            operands = {
                operand
                for operand in (left, right)
                if _VARIABLE.fullmatch(operand)
            }

            if not operands or target in operands:
                continue

            # Avoid potentially trapping operations.
            if operator in {"/", "%"}:
                continue

            # Every variable operand must remain unchanged in the loop.
            if any(
                _assigned(instruction) in operands
                for instruction in loop_instructions
            ):
                continue

            # The result must have exactly one assignment in the loop.
            if sum(
                _assigned(instruction) == target
                for instruction in loop_instructions
            ) != 1:
                continue

            # Only hoist assignments occurring before any conditional
            # instruction in their basic block.
            block = next(
                (
                    block_by_id[block_id]
                    for block_id in loop_blocks
                    if line in block_by_id[block_id]["instructions"]
                ),
                None,
            )

            if block is None:
                continue

            position = block["instructions"].index(line)

            if any(
                _CONDITIONAL.match(instruction)
                for instruction in block["instructions"][:position]
            ):
                continue

            candidates.append(line)

        if not candidates:
            continue

        # Hoist only when the header has no external conditional predecessor.
        external_preds = [
            predecessor
            for predecessor in cfg["predecessors"].get(header_id, [])
            if predecessor not in loop_blocks
        ]

        if not external_preds:
            continue

        
        # Remove the selected assignments from their original loop positions.
        moved_indices = []

        for block_id in loop_blocks:
            block = block_by_id[block_id]

            for offset, line in enumerate(block["instructions"]):
                if line in candidates:
                    moved_indices.append(block["start"] + offset)

        for index in sorted(moved_indices, reverse=True):
            result.pop(index)

        # Insert the assignments immediately before the loop header.
        result[header_start:header_start] = candidates


        # Rebuild the CFG after modifying instruction positions.
        try:
            cfg = build_cfg(result)
        except (ValueError, KeyError):
            return list(code)

        blocks = cfg["blocks"]
        block_by_id = {block["id"]: block for block in blocks}

    return result
