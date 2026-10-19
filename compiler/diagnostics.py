
"""Static semantic diagnostics for the Explainable Compiler."""

from .ast_nodes import (
    Assign,
    BinaryOp,
    Block,
    Declare,
    For,
    IfElse,
    Let,
    Print,
    UnaryOp,
    While,
    Number,
    Variable,
)


def _constant_value(expr):
    """Evaluate an expression only when it is safely constant."""
    if isinstance(expr, Number):
        return expr.value

    if isinstance(expr, UnaryOp):
        value = _constant_value(expr.operand)
        if value is None:
            return None
        if expr.op == "-":
            return -value
        if expr.op == "!":
            return int(not value)
        return None

    if isinstance(expr, BinaryOp):
        left = _constant_value(expr.left)
        right = _constant_value(expr.right)

        if left is None or right is None:
            return None

        try:
            if expr.op == "+":
                return left + right
            if expr.op == "-":
                return left - right
            if expr.op == "*":
                return left * right
            if expr.op == "/":
                return None if right == 0 else left / right
            if expr.op == "%":
                return None if right == 0 else left % right
        except (ArithmeticError, ValueError):
            return None

    return None


def _check_expression(expr, diagnostics):
    if isinstance(expr, BinaryOp):
        _check_expression(expr.left, diagnostics)
        _check_expression(expr.right, diagnostics)

        if expr.op in {"/", "%"}:
            divisor = _constant_value(expr.right)

            if divisor == 0:
                diagnostics.append({
                    "type": "division_by_zero",
                    "message": (
                        "Division or modulo by a constant zero "
                        "divisor is invalid."
                    ),
                    "operator": expr.op,
                    "position": expr.position,
                })

    elif isinstance(expr, UnaryOp):
        _check_expression(expr.operand, diagnostics)


def _check_statement(statement, diagnostics):
    if isinstance(statement, (Let, Declare, Assign, Print)):
        _check_expression(statement.value, diagnostics)

    elif isinstance(statement, Block):
        for item in statement.statements:
            _check_statement(item, diagnostics)

    elif isinstance(statement, IfElse):
        _check_expression(statement.condition, diagnostics)
        _check_statement(statement.then_branch, diagnostics)
        if statement.else_branch is not None:
            _check_statement(statement.else_branch, diagnostics)

    elif isinstance(statement, While):
        _check_expression(statement.condition, diagnostics)
        _check_statement(statement.body, diagnostics)

    elif isinstance(statement, For):
        if statement.initializer is not None:
            _check_statement(statement.initializer, diagnostics)
        if statement.condition is not None:
            _check_expression(statement.condition, diagnostics)
        if statement.update is not None:
            _check_statement(statement.update, diagnostics)
        _check_statement(statement.body, diagnostics)




def analyze_diagnostics(statements, source=None):
    """Return static semantic diagnostics with source locations."""
    diagnostics = []

    for statement in statements:
        _check_statement(statement, diagnostics)

    if source is not None:
        for diagnostic in diagnostics:
            position = diagnostic.get("position")

            if position is not None:
                diagnostic["line"] = source.count(
                    "\n", 0, position
                ) + 1

                last_newline = source.rfind("\n", 0, position)
                diagnostic["column"] = position - last_newline

    return diagnostics
