import sys
import os
import unittest

# Get the path to the project's root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from src import calculator


class TestCalculator(unittest.TestCase):
    """Unit tests for the arithmetic functions in src/calculator.py."""

    # ---------- Original arithmetic tests ----------

    def test_fun1(self):
        self.assertEqual(calculator.fun1(2, 3), 5)
        self.assertEqual(calculator.fun1(5, 0), 5)
        self.assertEqual(calculator.fun1(-1, 1), 0)
        self.assertEqual(calculator.fun1(-1, -1), -2)

    def test_fun2(self):
        self.assertEqual(calculator.fun2(2, 3), -1)
        self.assertEqual(calculator.fun2(5, 0), 5)
        self.assertEqual(calculator.fun2(-1, 1), -2)
        self.assertEqual(calculator.fun2(-1, -1), 0)

    def test_fun3(self):
        self.assertEqual(calculator.fun3(2, 3), 6)
        self.assertEqual(calculator.fun3(5, 0), 0)
        self.assertEqual(calculator.fun3(-1, 1), -1)
        self.assertEqual(calculator.fun3(-1, -1), 1)

    def test_fun4(self):
        self.assertEqual(calculator.fun4(2, 3, 5), 10)
        self.assertEqual(calculator.fun4(5, 0, -1), 4)
        self.assertEqual(calculator.fun4(-1, -1, -1), -3)
        self.assertEqual(calculator.fun4(-1, -1, 100), 98)

    # ---------- Tests for added functions ----------

    def test_fun5(self):
        self.assertEqual(calculator.fun5(10, 2), 5.0)
        self.assertEqual(calculator.fun5(7, 2), 3.5)
        self.assertEqual(calculator.fun5(-9, 3), -3.0)
        self.assertIsInstance(calculator.fun5(4, 2), float)

    def test_fun6(self):
        self.assertEqual(calculator.fun6(2, 3), 8)
        self.assertEqual(calculator.fun6(5, 0), 1)
        self.assertEqual(calculator.fun6(-2, 3), -8)
        self.assertEqual(calculator.fun6(9, 0.5), 3.0)

    def test_fun7(self):
        self.assertEqual(calculator.fun7(16), 4.0)
        self.assertEqual(calculator.fun7(0), 0.0)
        self.assertAlmostEqual(calculator.fun7(2), 1.41421356, places=6)

    # ---------- Input validation tests ----------

    def test_fun1_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun1("abc", 5)

    def test_fun2_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun2(5, None)

    def test_fun3_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun3([1, 2], 3)

    def test_fun4_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun4(1, 2, "three")

    def test_fun5_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun5(None, 2)

    def test_fun7_invalid_input(self):
        with self.assertRaises(ValueError):
            calculator.fun7("sixteen")

    def test_boolean_rejected(self):
        """Booleans are technically ints in Python, so reject them explicitly."""
        with self.assertRaises(ValueError):
            calculator.fun1(True, 5)

    # ---------- Domain error tests ----------

    def test_fun5_divide_by_zero(self):
        with self.assertRaises(ValueError):
            calculator.fun5(10, 0)

    def test_fun7_negative_input(self):
        with self.assertRaises(ValueError):
            calculator.fun7(-9)

    def test_error_message_content(self):
        with self.assertRaises(ValueError) as context:
            calculator.fun5(1, 0)
        self.assertIn("divide by zero", str(context.exception))

    # ---------- Additional assertion-method coverage ----------

    def test_not_equal(self):
        self.assertNotEqual(calculator.fun1(2, 2), 5)

    def test_truthiness(self):
        self.assertTrue(calculator.fun3(2, 3) > 0)
        self.assertFalse(calculator.fun3(2, 0) > 0)

    # ---------- Integration test ----------

    def test_chained_operations(self):
        a = calculator.fun1(2, 3)
        b = calculator.fun2(2, 3)
        c = calculator.fun3(2, 3)
        self.assertEqual(calculator.fun4(a, b, c), 10)


if __name__ == '__main__':
    unittest.main()