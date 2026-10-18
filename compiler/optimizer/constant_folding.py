"""Constant folding and basic constant propagation for TAC."""

import re
import ast
import operator


_ASSIGN = re.compile(r"^(\w+)\s*=\s*(.+)$")

_BINARY = re.compile(
    r"^(-?\d+(?:\.\d+)?)\s*"
    r"([+\-*/%])\s*"
    r"(-?\d+(?:\.\d+)?)$"
)

_OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _fold_expression(expression):
    match = _BINARY.fullmatch(expression.strip())

    if not match:
        return expression

    left, op, right = match.groups()
    a = float(left) if "." in left else int(left)
    b = float(right) if "." in right else int(right)

    if op in {"/", "%"} and b == 0:
        return expression

    try:
        result = _OPERATORS[op](a, b)
    except (ArithmeticError, OverflowError):
        return expression

    return _format_number(result)


def optimize(code: list[str]) -> list[str]:
    """Fold literal arithmetic expressions in TAC."""
    output = []

    for line in code:
        stripped = line.strip()

        # Keep labels and control-flow instructions unchanged.
        if (
            not stripped
            or stripped.endswith(":")
            or stripped.startswith(("goto ", "ifFalse ", "if "))
            or stripped.startswith("print ")
        ):
            output.append(line)
            continue

        match = _ASSIGN.fullmatch(stripped)

        if not match:
            output.append(line)
            continue

        target, expression = match.groups()
        folded = _fold_expression(expression)
        output.append(f"{target} = {folded}")

    return output


def constant_propagation(code: list[str]) -> list[str]:
    """Substitute known literal assignments into later TAC lines."""
    constants = {}
    output = []

    for line in code:
        stripped = line.strip()

        if not stripped or stripped.endswith(":"):
            output.append(line)
            continue

        # Do not propagate across control-flow boundaries.
        if stripped.startswith(("goto ", "if ", "ifFalse ")):
            output.append(line)
            constants.clear()
            continue

        if stripped.startswith("print "):
            value = stripped[len("print "):].strip()
            output.append(f"print {constants.get(value, value)}")
            continue

        match = _ASSIGN.fullmatch(stripped)

        if not match:
            output.append(line)
            continue

        target, expression = match.groups()

        for name, value in constants.items():
            expression = re.sub(
                rf"\b{re.escape(name)}\b",
                value,
                expression
            )

        expression = _fold_expression(expression)
        output.append(f"{target} = {expression}")

        if re.fullmatch(r"-?\d+(?:\.\d+)?", expression):
            constants[target] = expression
        else:
            constants.pop(target, None)

    return output