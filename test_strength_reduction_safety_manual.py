
from compiler.optimizer.strength_reduction import reduce_strength


def test_negative_multiplier_unchanged():
    code = ["x = y * -4"]
    assert reduce_strength(code) == code


def test_float_literal_unchanged():
    code = ["x = y * 4.0"]
    assert reduce_strength(code) == code


def test_variable_multiplier_unchanged():
    code = ["x = y * z"]
    assert reduce_strength(code) == code


def test_non_power_of_two_divisor_unchanged():
    code = ["x = y / 6"]
    assert reduce_strength(code) == code


def test_power_of_two_multiplication():
    code = ["x = y * 8"]
    assert reduce_strength(code) == ["x = y << 3"]
