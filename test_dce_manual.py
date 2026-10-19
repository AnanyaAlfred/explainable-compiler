
from compiler.optimizer.dead_code_elimination import eliminate_dead_assignments


def test_unused_assignment_removed():
    code = [
        "x = 10",
        "y = 20",
        "z = x + 5",
        "print z"
    ]

    result = eliminate_dead_assignments(code)

    assert "y = 20" not in result
    assert "x = 10" in result
    assert "z = x + 5" in result
    assert "print z" in result

    print("Unused assignment test passed!")


def test_chain_of_dead_assignments():
    code = [
        "a = 1",
        "b = a + 2",
        "c = b + 3",
        "print 7"
    ]

    result = eliminate_dead_assignments(code)

    assert result == ["print 7"]

    print("Dead assignment chain test passed!")


def test_branch_assignments_preserved():
    code = [
        "ifFalse c goto ELSE",
        "x = 1",
        "goto END",
        "ELSE:",
        "x = 2",
        "END:",
        "print x"
    ]

    result = eliminate_dead_assignments(code)

    assert "x = 1" in result
    assert "x = 2" in result
    assert "print x" in result

    print("Branch assignment test passed!")


def test_loop_assignments_preserved():
    code = [
        "i = 0",
        "LOOP:",
        "temp = 99",
        "x = i + 1",
        "i = x",
        "if i < 5 goto LOOP",
        "print i"
    ]

    result = eliminate_dead_assignments(code)

    assert "i = 0" in result
    assert "x = i + 1" in result
    assert "i = x" in result
    assert "if i < 5 goto LOOP" in result
    assert "print i" in result

    # This assignment has no effect on the loop's result.
    assert "temp = 99" not in result

    print("Loop DCE test passed!")



if __name__ == "__main__":
    test_unused_assignment_removed()
    test_chain_of_dead_assignments()
    test_branch_assignments_preserved()
    test_loop_assignments_preserved()
