
from compiler.optimizer.strength_reduction import reduce_strength


def test_multiply_by_power_of_two():
    code = ["x = y * 8"]

    assert reduce_strength(code) == ["x = y << 3"]



def test_divide_by_power_of_two():
    code = ["x = y / 4"]

    assert reduce_strength(code) == code


def test_non_power_of_two_unchanged():
    code = ["x = y * 6"]

    assert reduce_strength(code) == code


def test_zero_and_one_unchanged():
    code = [
        "x = y * 0",
        "z = y * 1",
    ]

    assert reduce_strength(code) == code


def test_labels_and_jumps_unchanged():
    code = [
        "LOOP:",
        "x = y * 8",
        "goto LOOP",
    ]

    assert reduce_strength(code) == [
        "LOOP:",
        "x = y << 3",
        "goto LOOP",
    ]
