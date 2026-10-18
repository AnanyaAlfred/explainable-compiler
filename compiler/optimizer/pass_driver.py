"""Driver for the initial optimization passes."""

from .constant_folding import optimize, constant_propagation
from .opportunities import detect_opportunities
from ..basic_blocks import partition_basic_blocks


def run_initial_passes(code: list[str]) -> dict:
    original = list(code)

    opportunities = detect_opportunities(original)

    after_folding = optimize(original)
    after_propagation = constant_propagation(after_folding)

    # Run folding again because propagation may expose new constants.
    final_code = optimize(after_propagation)

    return {
        "original_tac": original,
        "opportunities": opportunities,
        "pass_history": [
            {
                "pass_name": "constant_folding",
                "before": original,
                "after": after_folding
            },
            {
                "pass_name": "constant_propagation",
                "before": after_folding,
                "after": after_propagation
            },
            {
                "pass_name": "final_constant_folding",
                "before": after_propagation,
                "after": final_code
            }
        ],
        "optimized_tac": final_code,
        "basic_blocks": partition_basic_blocks(final_code)
    }