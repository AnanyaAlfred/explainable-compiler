"""Basic-block partitioning for linear TAC."""

import re


def partition_basic_blocks(code: list[str]) -> list[dict]:
    if not code:
        return []

    leaders = {0}
    label_positions = {}

    for index, line in enumerate(code):
        text = line.strip()

        if text.endswith(":"):
            label_positions[text[:-1]] = index
            leaders.add(index)

    for index, line in enumerate(code):
        text = line.strip()

        if text.startswith("goto "):
            label = text[len("goto "):].strip()
            if label in label_positions:
                leaders.add(label_positions[label])

            if index + 1 < len(code):
                leaders.add(index + 1)

        elif text.startswith(("if ", "ifFalse ")):
            match = re.search(r"\bgoto\s+(\w+)", text)
            if match and match.group(1) in label_positions:
                leaders.add(label_positions[match.group(1)])

            if index + 1 < len(code):
                leaders.add(index + 1)

    ordered = sorted(leaders)
    blocks = []

    for block_index, start in enumerate(ordered):
        end = (
            ordered[block_index + 1]
            if block_index + 1 < len(ordered)
            else len(code)
        )

        blocks.append({
            "id": f"B{block_index}",
            "start": start,
            "end": end,
            "instructions": code[start:end]
        })

    return blocks