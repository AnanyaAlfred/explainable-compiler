
from compiler.optimizer.common_subexpression import (
    eliminate_common_subexpressions,
)


def test_repeated_expression():
    code = [
        "a = b + c",
        "d = b + c",
        "print d",
    ]

    result = eliminate_common_subexpressions(code)

    assert result == [
        "a = b + c",
        "d = a",
        "print d",
    ]

    print("Repeated expression test passed!")


def test_reassignment_invalidates_expression():
    code = [
        "a = b + c",
        "b = 10",
        "d = b + c",
        "print d",
    ]

    result = eliminate_common_subexpressions(code)

    assert result[0] == "a = b + c"
    assert result[2] == "d = b + c"

    print("Reassignment invalidation test passed!")

def test_reassignment_of_result_invalidates_cache():
    code = [
        "a = b + c",
        "a = 10",
        "d = b + c",
        "print d"
    ]

    result = eliminate_common_subexpressions(code)

    assert result == [
        "a = b + c",
        "a = 10",
        "d = b + c",
        "print d"
    ]

    print("Result reassignment invalidation test passed!")


if __name__ == "__main__":
    test_repeated_expression()
    test_reassignment_invalidates_expression()
