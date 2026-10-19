
"""Strength reduction for simple integer TAC."""

import re

_BINARY_ASSIGNMENT = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*=\s*"
    r"([A-Za-z_]\w*|-?\d+)\s*"
    r"([*/])\s*(\d+)\s*$"
)


def reduce_strength(code: list[str]) -> list[str]:
    optimized = []

    for line in code:
        text = line.strip()
        match = _BINARY_ASSIGNMENT.fullmatch(text)

        if not match:
            optimized.append(line)
            continue

        target, operand, operator, literal = match.groups()
        number = int(literal)

        if operator != "*":
            optimized.append(line)
            continue

        if number <= 1 or number & (number - 1):
            optimized.append(line)
            continue

        shift = number.bit_length() - 1
        optimized.append(f"{target} = {operand} << {shift}")

    return optimized
