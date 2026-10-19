
from compiler.optimizer.loop_invariant import move_loop_invariants


def test_does_not_hoist_expression_using_operand_changed_in_loop():
    code = [
        "a = 5",
        "LOOP:",
        "t = a + 1",
        "a = a + 1",
        "if a < 10 goto LOOP",
        "END:",
        "print t",
    ]

    result = move_loop_invariants(code)

    assert result.index("t = a + 1") > result.index("LOOP:")


def test_does_not_hoist_across_conditional_loop_entry():
    code = [
        "ifFalse condition goto END",
        "a = 5",
        "LOOP:",
        "t = a + 1",
        "ifFalse again goto END",
        "goto LOOP",
        "END:",
        "print a",
    ]

    result = move_loop_invariants(code)

    assert result.index("t = a + 1") > result.index("LOOP:")


def test_moves_invariant_expression_only_once():
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

    assert result.count("t = a + b") == 1
    assert result.index("t = a + b") < result.index("LOOP:")
