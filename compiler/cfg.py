
"""Control Flow Graph construction from Three-Address Code."""

import re

from .basic_blocks import partition_basic_blocks


def build_cfg(code: list[str]) -> dict:
    """Build a CFG containing basic blocks, edges, successors and predecessors."""

    blocks = partition_basic_blocks(code)

    successors = {block["id"]: [] for block in blocks}
    predecessors = {block["id"]: [] for block in blocks}
    label_to_block = {}

    # Map each label to the basic block containing it.
    for block in blocks:
        for instruction in block["instructions"]:
            text = instruction.strip()

            if text.endswith(":"):
                label = text[:-1].strip()
                label_to_block[label] = block["id"]

    # Identify control-flow edges.
    edges = []

    for index, block in enumerate(blocks):
        block_id = block["id"]
        instructions = block["instructions"]

        # Find the last non-empty instruction.
        last_instruction = next(
            (
                line.strip()
                for line in reversed(instructions)
                if line.strip()
            ),
            ""
        )

        next_block = (
            blocks[index + 1]["id"]
            if index + 1 < len(blocks)
            else None
        )

        # Unconditional jump.
        if last_instruction.startswith("goto "):
            target_label = last_instruction[len("goto "):].strip()
            target_block = label_to_block.get(target_label)

            if target_block is None:
                raise ValueError(
                    f"Undefined jump target: {target_label}"
                )

            edges.append({
                "from": block_id,
                "to": target_block,
                "kind": "jump"
            })

        # Conditional jump: both the branch and fall-through are possible.
        elif re.match(r"^(if|ifFalse)\b.*\bgoto\s+", last_instruction):
            match = re.search(r"\bgoto\s+(\w+)", last_instruction)

            if match is None:
                raise ValueError(
                    f"Invalid conditional jump: {last_instruction}"
                )

            target_label = match.group(1)
            target_block = label_to_block.get(target_label)

            if target_block is None:
                raise ValueError(
                    f"Undefined jump target: {target_label}"
                )

            edges.append({
                "from": block_id,
                "to": target_block,
                "kind": "conditional"
            })

            if next_block is not None:
                edges.append({
                    "from": block_id,
                    "to": next_block,
                    "kind": "fallthrough"
                })

        # Ordinary instruction: execution continues to the next block.
        elif next_block is not None:
            edges.append({
                "from": block_id,
                "to": next_block,
                "kind": "fallthrough"
            })

    # Build adjacency lists from the edges.
    for edge in edges:
        source = edge["from"]
        target = edge["to"]

        if target not in successors[source]:
            successors[source].append(target)

        if source not in predecessors[target]:
            predecessors[target].append(source)

    return {
        "blocks": blocks,
        "edges": edges,
        "successors": successors,
        "predecessors": predecessors
    }
