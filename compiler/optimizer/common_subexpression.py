
"""Common subexpression elimination for simple TAC."""

import re


_BINARY_ASSIGNMENT = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*=\s*"
    r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*"
    r"([+\-*/%])\s*"
    r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*$"
)

_ASSIGNMENT = re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)")

def eliminate_common_subexpressions(code: list[str]) -> list[str]:
    output = []
    available = {}

    for line in code:
        text = line.strip()

        if not text or text.endswith(":") or text.startswith(("goto ", "if ", "ifFalse ")):
            output.append(line)
            available.clear()
            continue

        match = _BINARY_ASSIGNMENT.fullmatch(text)

        if match:
            target, left, operator, right = match.groups()

            if operator in {"+", "*"} and right < left:
                left, right = right, left

            expression = (left, operator, right)

            # Remove cached expressions invalidated by this assignment.
            available = {
                expr: variable
                for expr, variable in available.items()
                if variable != target and target not in (expr[0], expr[2])
            }

            if expression in available and target not in (left, right):
                source = available[expression]
                output.append(f"{target} = {source}")
                available[expression] = source
            else:
                output.append(line)

                # Don't cache expressions whose result assignment
                # changes one of their own operands.
                if target not in (left, right):
                    available[expression] = target

            continue

        assignment = _ASSIGNMENT.match(text)

        if assignment:
            target = assignment.group(1)

            available = {
                expr: variable
                for expr, variable in available.items()
                if variable != target and target not in (expr[0], expr[2])
            }

        output.append(line)

    return output
