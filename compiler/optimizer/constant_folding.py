"""Basic constant folding for three-address-code strings."""
import re

_BINARY = re.compile(r"^(\w+) = (-?\d+) ([+\-*/]) (-?\d+)$")

def optimize(code: list[str]) -> list[str]:
    """Fold operations whose operands are integer literals."""
    output = []
    for line in code:
        match = _BINARY.match(line.strip())
        if not match:
            output.append(line)
            continue
        target, left, op, right = match.groups()
        a, b = int(left), int(right)
        if op == "+": value = a + b
        elif op == "-": value = a - b
        elif op == "*": value = a * b
        elif op == "/" and b != 0: value = int(a / b)
        else:
            output.append(line)
            continue
        output.append(f"{target} = {value}")
    return output
