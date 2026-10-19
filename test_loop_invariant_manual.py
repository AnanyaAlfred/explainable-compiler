
from compiler.optimizer.loop_invariant import (
    move_loop_invariants,
    analyze_licm_safety,
)


def test_keeps_modified_operand_inside_loop():
    code = [
        "a = 5",
        "LOOP:",
        "a = a + 1",
        "t = a * 2",
        "if a < 10 goto LOOP",
    ]

    result = move_loop_invariants(code)

    assert "t = a * 2" in result
    assert result.index("t = a * 2") > result.index("LOOP:")


def test_no_loop_unchanged():
    code = [
        "a = 5",
        "t = a + 2",
        "print t",
    ]

    assert move_loop_invariants(code) == code

def test_moves_invariant_expression_before_loop():
    code = [
        "a = 5",
        "b = 10",
        "LOOP:",
        "t = a + b",
        "x = x + t",
        "if x < 100 goto LOOP",
        "goto END",
        "END:",
        "print x",
    ]

    result = move_loop_invariants(code)

    assert result == [
        "a = 5",
        "b = 10",
        "t = a + b",
        "LOOP:",
        "x = x + t",
        "if x < 100 goto LOOP",
        "goto END",
        "END:",
        "print x",
    ]

def test_safety_report_explains_hoisted_invariant():
    code = [
        "a = 5",
        "b = 10",
        "LOOP:",
        "t = a + b",
        "x = x + t",
        "if x < 100 goto LOOP",
        "goto END",
        "END:",
        "print x",
    ]

    report = analyze_licm_safety(code)

    assert any(
        item["instruction"] == "t = a + b"
        and item["decision"] == "safe"
        and item["reason"]
        for item in report
    )


if __name__ == "__main__":
    test_moves_invariant_expression()
    test_keeps_modified_operand_inside_loop()
    test_no_loop_unchanged()
    print("All LICM tests passed!")
