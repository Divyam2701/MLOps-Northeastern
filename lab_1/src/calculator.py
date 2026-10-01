import math


def _validate_numbers(*args):
    """
    Validates that all arguments are numeric (int or float, not bool).

    Args:
        *args: Values to validate.

    Raises:
        ValueError: If any argument is not a number.
    """
    for value in args:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("All inputs must be numbers.")


def fun1(x, y):
    """
    Adds two numbers together.

    Args:
        x (int/float): First number.
        y (int/float): Second number.

    Returns:
        int/float: Sum of x and y.

    Raises:
        ValueError: If x or y is not a number.
    """
    _validate_numbers(x, y)
    return x + y


def fun2(x, y):
    """
    Subtracts y from x.

    Args:
        x (int/float): First number.
        y (int/float): Second number.

    Returns:
        int/float: Difference of x and y.

    Raises:
        ValueError: If x or y is not a number.
    """
    _validate_numbers(x, y)
    return x - y


def fun3(x, y):
    """
    Multiplies two numbers together.

    Args:
        x (int/float): First number.
        y (int/float): Second number.

    Returns:
        int/float: Product of x and y.

    Raises:
        ValueError: If x or y is not a number.
    """
    _validate_numbers(x, y)
    return x * y


def fun4(x, y, z):
    """
    Adds three numbers together.

    Args:
        x (int/float): First number.
        y (int/float): Second number.
        z (int/float): Third number.

    Returns:
        int/float: Sum of x, y and z.

    Raises:
        ValueError: If any input is not a number.
    """
    _validate_numbers(x, y, z)
    return x + y + z


def fun5(x, y):
    """
    Divides x by y.

    Args:
        x (int/float): Numerator.
        y (int/float): Denominator.

    Returns:
        float: Quotient of x and y.

    Raises:
        ValueError: If x or y is not a number, or if y is zero.
    """
    _validate_numbers(x, y)
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y


def fun6(x, y):
    """
    Raises x to the power of y.

    Args:
        x (int/float): Base.
        y (int/float): Exponent.

    Returns:
        int/float: x raised to the power y.

    Raises:
        ValueError: If x or y is not a number.
    """
    _validate_numbers(x, y)
    return x ** y


def fun7(x):
    """
    Computes the square root of x.

    Args:
        x (int/float): Number to take the square root of.

    Returns:
        float: Square root of x.

    Raises:
        ValueError: If x is not a number or is negative.
    """
    _validate_numbers(x)
    if x < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    return math.sqrt(x)