
"""Copy propagation for simple TAC assignments."""

import re

_ASSIGNMENT = re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.*?)\s*$")
_VARIABLE = re.compile(r"^[A-Za-z_]\w*$")



def propagate_copies(code: list[str]) -> list[str]:
    output = []
    copies = {}

    def resolve(variable):
        seen = set()

        while variable in copies and variable not in seen:
            seen.add(variable)
            variable = copies[variable]

        return variable

    for line in code:
        text = line.strip()

        if not text or text.endswith(":") or text.startswith(
            ("goto ", "if ", "ifFalse ")
        ):
            output.append(line)
            copies.clear()
            continue

        match = _ASSIGNMENT.match(text)

        if not match:
            output.append(line)
            continue

        target, rhs = match.groups()

        # Substitute currently valid copies into the RHS.
        rhs = re.sub(
            r"\b[A-Za-z_]\w*\b",
            lambda m: (
                m.group(0)
                if m.group(0) in {"true", "false", "null", "None"}
                else resolve(m.group(0))
            ),
            rhs,
        )

        # Invalidate copies affected by overwriting the target.
        copies = {
            variable: source
            for variable, source in copies.items()
            if variable != target and source != target
        }

        output.append(f"{target} = {rhs}")

        # Track a new copy only when the RHS is a variable.
        if _VARIABLE.fullmatch(rhs) and rhs != target:
            copies[target] = resolve(rhs)

    return output
