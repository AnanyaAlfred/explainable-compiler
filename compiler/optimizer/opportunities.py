"""Static scanner for potential TAC optimization opportunities."""

import re


def detect_opportunities(code: list[str]) -> list[dict]:
    opportunities = []
    seen_expressions = {}

    for index, line in enumerate(code):
        text = line.strip()


        # Detect division or modulo by zero.
        zero_divisor_match = re.search(
            r"=\s*[^=].*?\s*([/%])\s*0(?:\.0+)?\s*$",
            text
        )

        if zero_divisor_match:
            operator = zero_divisor_match.group(1)

            opportunities.append({
                "type": "division_by_zero",
                "line": index,
                "instruction": text,
                "why": (
                    "The expression divides or takes a remainder "
                    "using zero as the divisor."
                ),
                "suggestion": (
                    "Handle the zero divisor before evaluating this "
                    "expression."
                )
            })


        # Constant folding.

        constant_match = re.search(
            r"=\s*(-?\d+(?:\.\d+)?)\s*([+\-*/%])\s*"
            r"(-?\d+(?:\.\d+)?)$",
            text
        )

        if constant_match:
            left, operator, right = constant_match.groups()

            is_zero_divisor = (
                operator in {"/", "%"} and float(right) == 0
            )

            if not is_zero_divisor:
                opportunities.append({
                    "type": "constant_folding",
                    "line": index,
                    "instruction": text,
                    "why": "Both operands are numeric constants.",
                    "suggestion": (
                        "Evaluate the expression at compile time."
                    )
                })


        # Algebraic simplifications.
        if re.search(r"=\s*\w+\s*\+\s*0$", text):
            opportunities.append({
                "type": "algebraic_simplification",
                "line": index,
                "instruction": text,
                "why": "Adding zero does not change the value.",
                "suggestion": "Replace the expression with its nonzero operand."
            })

        if re.search(r"=\s*\w+\s*\*\s*1$", text):
            opportunities.append({
                "type": "algebraic_simplification",
                "line": index,
                "instruction": text,
                "why": "Multiplication by one preserves the value.",
                "suggestion": "Replace the expression with its other operand."
            })

        # Common subexpression candidates.

        # Reset expression history at control-flow boundaries.
        if (
            text.endswith(":")
            or text.startswith(("goto ", "if ", "ifFalse "))
        ):
            seen_expressions.clear()
            continue

        # Common subexpression candidates.
        match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=\s*"
            r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*"
            r"([+\-*/])\s*"
            r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)",
            text
        )

        if match:
            target, left, op, right = match.groups()

            # Addition and multiplication are commutative.
            if op in {"+", "*"}:
                operands = tuple(sorted((left, right)))
            else:
                operands = (left, right)

            expression = (op, *operands)

            if expression in seen_expressions:
                opportunities.append({
                    "type": "common_subexpression",
                    "line": index,
                    "instruction": text,
                    "why": (
                        "The same expression appeared earlier in the "
                        "current straight-line region."
                    ),
                    "suggestion": (
                        "Consider reusing the earlier result after "
                        "checking that neither operand has changed."
                    ),
                    "previous_line": seen_expressions[expression]
                })
            else:
                seen_expressions[expression] = index

        # Invalidate expressions that depend on a reassigned variable.
        assignment = re.match(
            r"^\s*([A-Za-z_]\w*)\s*=(?!=)",
            text
        )

        if assignment:
            defined = assignment.group(1)

            seen_expressions = {
                expression: previous_line
                for expression, previous_line in seen_expressions.items()
                if defined not in expression[1:]
            }


        # Strength reduction: multiplication by a positive power of two.
        strength_match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=\s*"
            r"([A-Za-z_]\w*|-?\d+)\s*\*\s*(\d+)",
            text
        )

        if strength_match:
            target, operand, literal = strength_match.groups()
            number = int(literal)

            if number > 1 and (number & (number - 1)) == 0:
                shift = number.bit_length() - 1

                opportunities.append({
                    "type": "strength_reduction",
                    "line": index,
                    "instruction": text,
                    "why": (
                        f"Multiplication by {number}, a power of two, "
                        "can potentially be replaced with a left shift."
                    ),
                    "suggestion": (
                        f"Consider replacing the multiplication with "
                        f"{target} = {operand} << {shift}, provided "
                        "the target language's integer and overflow "
                        "semantics make the transformation equivalent."
                    )
                })



        # Copy propagation candidates: x = y, where y is a variable.
        copy_match = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)",
            text
        )

        if copy_match:
            left, right = copy_match.groups()

            if left != right:
                opportunities.append({
                    "type": "copy_propagation",
                    "line": index,
                    "instruction": text,
                    "why": "The assignment copies another variable.",
                    "suggestion": (
                        "Consider substituting the source variable "
                        "where it remains valid."
                    )
                })
    return opportunities