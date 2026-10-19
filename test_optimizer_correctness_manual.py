
from compiler.optimizer.common_subexpression import eliminate_common_subexpressions
from compiler.optimizer.copy_propagation import propagate_copies


def test_cse_result_survives_reassignment():
    code = [
        "a = b + c",
        "a = 10",
        "d = b + c",
        "print d",
    ]

    result = eliminate_common_subexpressions(code)

    assert result == [
        "a = b + c",
        "a = 10",
        "d = b + c",
        "print d",
    ]


def test_copy_propagation_after_source_reassignment():
    code = [
        "a = b",
        "b = 10",
        "c = a + b",
    ]

    result = propagate_copies(code)

    # a must not be replaced with the new value of b.
    assert result == [
        "a = b",
        "b = 10",
        "c = a + b",
    ]


def test_copy_chain():
    code = [
        "a = b",
        "c = a",
        "d = c + 1",
    ]

    result = propagate_copies(code)

    assert result == [
        "a = b",
        "c = b",
        "d = b + 1",
    ]
