
from compiler.optimizer.loop_invariant import move_loop_invariants


def test_does_not_move_modified_operand():
    code = [
        "a = 5",
        "LOOP:",
        "a = a + 1",
        "t = a * 2",
        "if a < 10 goto LOOP",
    ]

    result = move_loop_invariants(code)

    assert result.index("t = a * 2") > result.index("LOOP:")


def test_does_not_move_expression_with_loop_defined_operand():
    code = [
        "LOOP:",
        "a = 5",
        "t = a + 2",
        "if a < 10 goto LOOP",
    ]

    result = move_loop_invariants(code)

    assert result.index("t = a + 2") > result.index("LOOP:")


def test_preserves_code_without_loop():
    code = [
        "a = 5",
        "t = a + 2",
        "print t",
    ]

    assert move_loop_invariants(code) == code


def test_does_not_hoist_expression_past_a_loop_skip():
    code = [
        "a = 5",
        "ifFalse condition goto END",
        "LOOP:",
        "t = a + 1",
        "ifFalse again goto END",
        "goto LOOP",
        "END:",
        "print a",
    ]

    result = move_loop_invariants(code)

    assert result.index("t = a + 1") > result.index("LOOP:")
