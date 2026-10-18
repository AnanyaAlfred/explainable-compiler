"""Static scanner for potential TAC optimization opportunities."""

import re


def detect_opportunities(code: list[str]) -> list[dict]:
    opportunities = []
    seen_expressions = {}

    for index, line in enumerate(code):
        text = line.strip()

        # Constant folding.
        if re.search(
            r"=\s*-?\d+(?:\.\d+)?\s*[+\-*/%]\s*"
            r"-?\d+(?:\.\d+)?$",
            text
        ):
            opportunities.append({
                "type": "constant_folding",
                "line": index,
                "instruction": text,
                "why": "Both operands are numeric constants.",
                "suggestion": "Evaluate the expression at compile time."
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
        match = re.fullmatch(
            r"(\w+)\s*=\s*(\w+)\s*([+\-*/])\s*(\w+)",
            text
        )

        if match:
            target, left, op, right = match.groups()
            expression = (op, left, right)

            if expression in seen_expressions:
                opportunities.append({
                    "type": "common_subexpression",
                    "line": index,
                    "instruction": text,
                    "why": "The same expression appeared earlier.",
                    "suggestion": (
                        "Consider reusing the earlier result after "
                        "checking that operands have not changed."
                    ),
                    "previous_line": seen_expressions[expression]
                })
            else:
                seen_expressions[expression] = index

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