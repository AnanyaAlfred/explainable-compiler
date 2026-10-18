"""Three-address-code generator."""

from .ast_nodes import (
    Assign, BinaryOp, Block, Declare, For,
    IfElse, Let, Number, Print, UnaryOp,
    Variable, While
)


def generate(statements):
    code = []
    temp_counter = 0
    label_counter = 0

    def new_temp():
        nonlocal temp_counter
        name = f"t{temp_counter}"
        temp_counter += 1
        return name

    def new_label(prefix="L"):
        nonlocal label_counter
        name = f"{prefix}{label_counter}"
        label_counter += 1
        return name

    def expr(node):
        if isinstance(node, Number):
            return str(node.value)

        if isinstance(node, Variable):
            return node.name

        if isinstance(node, UnaryOp):
            operand = expr(node.operand)
            temp = new_temp()
            code.append(f"{temp} = {node.op}{operand}")
            return temp

        if isinstance(node, BinaryOp):
            left = expr(node.left)
            right = expr(node.right)
            temp = new_temp()
            code.append(f"{temp} = {left} {node.op} {right}")
            return temp

        raise TypeError(f"Unsupported expression: {node!r}")

    def emit_statement(statement):
        if isinstance(statement, Let):
            code.append(
                f"{statement.name} = {expr(statement.value)}"
            )

        elif isinstance(statement, Declare):
            code.append(
                f"{statement.name} = {expr(statement.value)}"
            )

        elif isinstance(statement, Assign):
            code.append(
                f"{statement.name} = {expr(statement.value)}"
            )

        elif isinstance(statement, Print):
            code.append(f"print {expr(statement.value)}")

        elif isinstance(statement, Block):
            emit_statements(statement.statements)

        elif isinstance(statement, IfElse):
            condition = expr(statement.condition)
            else_label = new_label("ELSE")
            end_label = new_label("ENDIF")

            code.append(f"ifFalse {condition} goto {else_label}")
            emit_statement(statement.then_branch)
            code.append(f"goto {end_label}")
            code.append(f"{else_label}:")

            if statement.else_branch is not None:
                emit_statement(statement.else_branch)

            code.append(f"{end_label}:")

        elif isinstance(statement, While):
            start_label = new_label("WHILE")
            end_label = new_label("ENDWHILE")

            code.append(f"{start_label}:")
            condition = expr(statement.condition)
            code.append(f"ifFalse {condition} goto {end_label}")
            emit_statement(statement.body)
            code.append(f"goto {start_label}")
            code.append(f"{end_label}:")

        elif isinstance(statement, For):
            if statement.initializer is not None:
                emit_statement(statement.initializer)

            start_label = new_label("FOR")
            end_label = new_label("ENDFOR")

            code.append(f"{start_label}:")

            if statement.condition is not None:
                condition = expr(statement.condition)
                code.append(f"ifFalse {condition} goto {end_label}")

            emit_statement(statement.body)

            if statement.update is not None:
                emit_statement(statement.update)

            code.append(f"goto {start_label}")
            code.append(f"{end_label}:")

        else:
            raise TypeError(f"Unsupported statement: {statement!r}")

    def emit_statements(items):
        for item in items:
            emit_statement(item)

    emit_statements(statements)
    return code