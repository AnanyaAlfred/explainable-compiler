
from compiler.optimizer.pass_driver import run_initial_passes


def test_pipeline_records_all_passes():
    code = [
        "a = 2 + 3",
        "b = a * 4",
        "c = b",
        "print c",
    ]

    result = run_initial_passes(code)

    assert result["original_tac"] == code
    assert result["optimized_tac"]
    assert result["basic_blocks"]
    assert len(result["pass_history"]) == 8

    names = [item["pass_name"] for item in result["pass_history"]]

    assert names == [
        "constant_folding",
        "constant_propagation",
        "final_constant_folding",
        "common_subexpression_elimination",
        "copy_propagation",
        "strength_reduction",
        "loop_invariant_code_motion",
        "dead_code_elimination",
    ]
