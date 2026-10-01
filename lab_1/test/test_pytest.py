import pytest
from src import calculator


# ---------- Original arithmetic tests ----------

def test_fun1():
    assert calculator.fun1(2, 3) == 5
    assert calculator.fun1(5, 0) == 5
    assert calculator.fun1(-1, 1) == 0
    assert calculator.fun1(-1, -1) == -2


def test_fun2():
    assert calculator.fun2(2, 3) == -1
    assert calculator.fun2(5, 0) == 5
    assert calculator.fun2(-1, 1) == -2
    assert calculator.fun2(-1, -1) == 0


def test_fun3():
    assert calculator.fun3(2, 3) == 6
    assert calculator.fun3(5, 0) == 0
    assert calculator.fun3(-1, 1) == -1
    assert calculator.fun3(-1, -1) == 1


def test_fun4():
    assert calculator.fun4(2, 3, 5) == 10
    assert calculator.fun4(5, 0, -1) == 4
    assert calculator.fun4(-1, -1, -1) == -3
    assert calculator.fun4(-1, -1, 100) == 98


# ---------- Tests for added functions ----------

def test_fun5():
    assert calculator.fun5(10, 2) == 5.0
    assert calculator.fun5(7, 2) == 3.5
    assert calculator.fun5(-9, 3) == -3.0
    assert isinstance(calculator.fun5(4, 2), float)


def test_fun6():
    assert calculator.fun6(2, 3) == 8
    assert calculator.fun6(5, 0) == 1
    assert calculator.fun6(-2, 3) == -8
    assert calculator.fun6(9, 0.5) == 3.0


def test_fun7():
    assert calculator.fun7(16) == 4.0
    assert calculator.fun7(0) == 0.0
    assert calculator.fun7(2) == pytest.approx(1.41421356, rel=1e-6)


# ---------- Parametrized tests ----------

@pytest.mark.parametrize("x, y, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (2.5, 2.5, 5.0),
    (-10, -5, -15),
    (100, 0.5, 100.5),
])
def test_fun1_parametrized(x, y, expected):
    assert calculator.fun1(x, y) == expected


@pytest.mark.parametrize("x, y, expected", [
    (10, 2, 5.0),
    (9, 3, 3.0),
    (1, 4, 0.25),
    (-6, 2, -3.0),
])
def test_fun5_parametrized(x, y, expected):
    assert calculator.fun5(x, y) == expected


# ---------- Input validation tests ----------

@pytest.mark.parametrize("bad_input", ["abc", None, [1, 2], True, {"a": 1}, (1,)])
def test_fun1_rejects_non_numbers(bad_input):
    with pytest.raises(ValueError):
        calculator.fun1(bad_input, 5)


@pytest.mark.parametrize("bad_input", ["abc", None, [1, 2], True])
def test_fun2_rejects_non_numbers(bad_input):
    with pytest.raises(ValueError):
        calculator.fun2(5, bad_input)


def test_fun3_rejects_non_numbers():
    with pytest.raises(ValueError):
        calculator.fun3("2", 3)


def test_fun4_rejects_non_numbers():
    with pytest.raises(ValueError):
        calculator.fun4(1, 2, "three")


def test_fun5_rejects_non_numbers():
    with pytest.raises(ValueError):
        calculator.fun5(None, 2)


def test_fun7_rejects_non_numbers():
    with pytest.raises(ValueError):
        calculator.fun7("sixteen")


# ---------- Domain error tests ----------

def test_fun5_divide_by_zero():
    with pytest.raises(ValueError):
        calculator.fun5(10, 0)


def test_fun7_negative_input():
    with pytest.raises(ValueError):
        calculator.fun7(-4)


def test_error_message_content():
    with pytest.raises(ValueError, match="divide by zero"):
        calculator.fun5(1, 0)


# ---------- Integration test ----------

def test_chained_operations():
    """Mirrors the commented-out usage example in calculator.py."""
    a = calculator.fun1(2, 3)   # 5
    b = calculator.fun2(2, 3)   # -1
    c = calculator.fun3(2, 3)   # 6
    assert calculator.fun4(a, b, c) == 10