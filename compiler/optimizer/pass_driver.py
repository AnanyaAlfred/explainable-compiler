
"""Driver for the optimization passes."""

from .constant_folding import optimize, constant_propagation
from .opportunities import detect_opportunities
from .dead_code_elimination import eliminate_dead_assignments
from .common_subexpression import eliminate_common_subexpressions
from .copy_propagation import propagate_copies
from .strength_reduction import reduce_strength
from .loop_invariant import move_loop_invariants
from ..basic_blocks import partition_basic_blocks
from .loop_invariant import analyze_licm_safety


def run_initial_passes(code: list[str]) -> dict:
    original = list(code)
    opportunities = detect_opportunities(original)

    after_folding = optimize(original)
    after_propagation = constant_propagation(after_folding)
    after_final_folding = optimize(after_propagation)
    after_cse = eliminate_common_subexpressions(after_final_folding)
    after_copy_propagation = propagate_copies(after_cse)
    after_strength_reduction = reduce_strength(after_copy_propagation)
    licm_safety = analyze_licm_safety(after_strength_reduction)
    after_licm = move_loop_invariants(after_strength_reduction)
    after_dce = eliminate_dead_assignments(after_licm)

    pass_history = [
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
            "after": after_final_folding
        },
        {
            "pass_name": "common_subexpression_elimination",
            "before": after_final_folding,
            "after": after_cse
        },
        {
            "pass_name": "copy_propagation",
            "before": after_cse,
            "after": after_copy_propagation
        },
        {
            "pass_name": "strength_reduction",
            "before": after_copy_propagation,
            "after": after_strength_reduction
        },
        {
            "pass_name": "loop_invariant_code_motion",
            "before": after_strength_reduction,
            "after": after_licm
        },
        {
            "pass_name": "dead_code_elimination",
            "before": after_licm,
            "after": after_dce
        }
    ]

    return {
        "original_tac": original,
        "opportunities": opportunities,
        "pass_history": pass_history,
        "optimized_tac": after_dce,
        "licm_safety": licm_safety,
        "basic_blocks": partition_basic_blocks(after_dce)
    }
