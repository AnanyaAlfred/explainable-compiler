
from compiler.optimizer.copy_propagation import propagate_copies


def test_simple_copy():
    code = [
        "a = b",
        "c = a + 10",
        "print c",
    ]

    result = propagate_copies(code)

    assert result == [
        "a = b",
        "c = b + 10",
        "print c",
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


def test_reassignment_invalidates_copy():
    code = [
        "a = b",
        "b = 10",
        "c = a + b",
    ]

    result = propagate_copies(code)

    assert result == [
        "a = b",
        "b = 10",
        "c = a + b",
    ]


if __name__ == "__main__":
    test_simple_copy()
    test_copy_chain()
    test_reassignment_invalidates_copy()
    print("All copy propagation tests passed!")
