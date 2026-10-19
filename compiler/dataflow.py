
"""Basic dataflow information for TAC basic blocks."""

import re

def _defined_variable(instruction: str) -> str | None:
    """Return the assigned variable for a simple TAC assignment."""
    text = instruction.strip()

    if not text or text.endswith(":"):
        return None

    match = re.match(r"^([A-Za-z_]\w*)\s*=(?!=)", text)
    return match.group(1) if match else None



def _used_variables(instruction: str) -> set[str]:
    """Return variables used by a TAC instruction, excluding labels."""
    text = instruction.strip()

    if not text or text.endswith(":"):
        return set()

    # A jump target is a label, not a variable.
    if text.startswith("goto "):
        return set()

    if text.startswith(("if ", "ifFalse ")):
        match = re.search(r"\bgoto\s+(\w+)", text)
        if match:
            text = text[:match.start()]

    # Ignore the left-hand side of an assignment.
    match = re.match(r"^([A-Za-z_]\w*)\s*=(?!=)", text)
    if match:
        text = text[match.end():]

    ignored = {
        "goto", "if", "ifFalse", "print", "return",
        "true", "false", "null", "None"
    }

    return {
        name
        for name in re.findall(r"\b[A-Za-z_]\w*\b", text)
        if name not in ignored
    }


def compute_use_def(blocks: list[dict]) -> dict[str, dict[str, set[str]]]:
    """Compute block-level USE and DEF sets."""
    result = {}

    for block in blocks:
        block_id = block["id"]
        use = set()
        defined = set()

        for instruction in block["instructions"]:
            uses = _used_variables(instruction)
            definition = _defined_variable(instruction)

            # A use belongs to USE only if not previously defined in this block.
            use.update(uses - defined)

            if definition is not None:
                defined.add(definition)

        result[block_id] = {
            "USE": use,
            "DEF": defined
        }

    return result


def compute_liveness(
    blocks: list[dict],
    use_def: dict[str, dict[str, set[str]]],
    cfg: dict
) -> dict[str, dict[str, set[str]]]:
    """Compute live-variable IN and OUT sets using backward dataflow analysis."""
    live_in = {block["id"]: set() for block in blocks}
    live_out = {block["id"]: set() for block in blocks}

    successors = cfg["successors"]
    changed = True

    while changed:
        changed = False

        for block in reversed(blocks):
            block_id = block["id"]

            new_out = set()
            for successor in successors.get(block_id, []):
                new_out.update(live_in[successor])

            new_in = use_def[block_id]["USE"] | (
                new_out - use_def[block_id]["DEF"]
            )

            if new_out != live_out[block_id] or new_in != live_in[block_id]:
                live_out[block_id] = new_out
                live_in[block_id] = new_in
                changed = True

    return {
        block_id: {
            "IN": live_in[block_id],
            "OUT": live_out[block_id]
        }
        for block_id in live_in
    }

def compute_def_use_chains(blocks: list[dict], cfg: dict) -> dict:
    """Link each variable definition to instructions it may reach and be used by."""
    predecessors = cfg["predecessors"]
    block_ids = [block["id"] for block in blocks]

    # Reaching definitions: each definition is (block_id, instruction_index, variable).
    gen = {}
    kill = {}

    for block in blocks:
        block_id = block["id"]
        block_gen = {}
        block_kill = set()

        for index, instruction in enumerate(block["instructions"]):
            variable = _defined_variable(instruction)
            if variable is None:
                continue

            block_kill.update(
                definition
                for definition in block_gen.values()
                if definition[2] == variable
            )
            block_gen[variable] = (block_id, index, variable)

        gen[block_id] = set(block_gen.values())
        kill[block_id] = block_kill

    # Reaching-definition fixed-point analysis.
    reaching_in = {block_id: set() for block_id in block_ids}
    reaching_out = {block_id: set() for block_id in block_ids}

    all_definitions = {
        definition
        for definitions in gen.values()
        for definition in definitions
    }

    changed = True
    while changed:
        changed = False

        for block in blocks:
            block_id = block["id"]

            new_in = set()
            for predecessor in predecessors.get(block_id, []):
                new_in.update(reaching_out[predecessor])

            block_gen = gen[block_id]
            defined_variables = {definition[2] for definition in block_gen}
            new_out = {
                definition
                for definition in new_in
                if definition[2] not in defined_variables
            } | block_gen

            if (
                new_in != reaching_in[block_id]
                or new_out != reaching_out[block_id]
            ):
                reaching_in[block_id] = new_in
                reaching_out[block_id] = new_out
                changed = True

    # Collect definition-to-use links at instruction level.
    chains = []

    for block in blocks:
        block_id = block["id"]
        reaching = set(reaching_in[block_id])

        for index, instruction in enumerate(block["instructions"]):
            for variable in _used_variables(instruction):
                for definition in reaching:
                    if definition[2] == variable:
                        chains.append({
                            "variable": variable,
                            "definition": {
                                "block": definition[0],
                                "instruction_index": definition[1],
                            },
                            "use": {
                                "block": block_id,
                                "instruction_index": index,
                            },
                        })

            defined_variable = _defined_variable(instruction)
            if defined_variable is not None:
                reaching = {
                    definition
                    for definition in reaching
                    if definition[2] != defined_variable
                }
                reaching.add((block_id, index, defined_variable))

    return {
        "reaching_in": reaching_in,
        "reaching_out": reaching_out,
        "chains": chains,
    }