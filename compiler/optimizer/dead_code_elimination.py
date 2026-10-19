
"""CFG-aware dead-code elimination for simple TAC assignments."""

import re

from ..basic_blocks import partition_basic_blocks
from ..cfg import build_cfg
from ..dataflow import compute_use_def, compute_liveness


def _assigned_variable(instruction: str) -> str | None:
    match = re.match(r"^\s*([A-Za-z_]\w*)\s*=(?!=)", instruction)
    return match.group(1) if match else None


def _used_variables(instruction: str) -> set[str]:
    text = instruction.strip()

    if not text or text.endswith(":") or text.startswith("goto "):
        return set()

    if text.startswith(("if ", "ifFalse ")):
        match = re.search(r"\bgoto\s+(\w+)", text)
        if match:
            text = text[:match.start()]

    match = re.match(r"^([A-Za-z_]\w*)\s*=(?!=)", text)
    if match:
        text = text[match.end():]

    ignored = {
        "goto", "if", "ifFalse", "print", "return",
        "true", "false", "null", "None"
    }

    return {
        name for name in re.findall(r"\b[A-Za-z_]\w*\b", text)
        if name not in ignored
    }



def eliminate_dead_assignments(code: list[str]) -> list[str]:
    """Remove dead assignments using iterative CFG-based liveness."""
    optimized = list(code)

    while True:
        previous = optimized.copy()

        blocks = partition_basic_blocks(optimized)
        if not blocks:
            return []

        cfg = build_cfg(optimized)
        use_def = compute_use_def(blocks)
        liveness = compute_liveness(blocks, use_def, cfg)

        # Process blocks backwards so removals don't invalidate
        # the original positions of blocks still to be processed.
        for block in reversed(blocks):
            block_id = block["id"]
            live = set(liveness[block_id]["OUT"])
            kept_reversed = []

            for instruction in reversed(block["instructions"]):
                assigned = _assigned_variable(instruction)
                used = _used_variables(instruction)

                if assigned is not None and assigned not in live:
                    rhs = instruction.split("=", 1)[1].strip()

                    # Preserve potentially effectful expressions.
                    if not any(
                        token in rhs for token in ("(", "++", "--")
                    ):
                        continue

                if assigned is not None:
                    live.discard(assigned)

                live.update(used)
                kept_reversed.append(instruction)

            optimized[block["start"]:block["end"]] = reversed(
                kept_reversed
            )

        # Stop when another pass removes no additional instructions.
        if optimized == previous:
            return optimized
