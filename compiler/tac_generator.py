"""Three-address-code generator."""
from .ast_nodes import BinaryOp, Let, Number, Print, Variable

def generate(statements):
    code = []
    temp_counter = 0

    def expr(node):
        nonlocal temp_counter
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, Variable):
            return node.name
        if isinstance(node, BinaryOp):
            left, right = expr(node.left), expr(node.right)
            temp = f"t{temp_counter}"
            temp_counter += 1
            code.append(f"{temp} = {left} {node.op} {right}")
            return temp
        raise TypeError(f"Unsupported expression: {node!r}")

    for statement in statements:
        if isinstance(statement, Let):
            code.append(f"{statement.name} = {expr(statement.value)}")
        elif isinstance(statement, Print):
            code.append(f"print {expr(statement.value)}")
        else:
            raise TypeError(f"Unsupported statement: {statement!r}")
    return code
