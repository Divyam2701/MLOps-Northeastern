# MLOps Lab 1 — Unit Testing and CI/CD

A calculator module with input validation, tested with both `pytest` and
`unittest`, running on a GitHub Actions pipeline with a coverage gate.

## Modifications from the original lab

**Source code**
- Added `fun5` (division), `fun6` (exponentiation), `fun7` (square root)
- Added input validation to all functions via a shared `_validate_numbers`
  helper, raising `ValueError` on non-numeric input
- Rejected booleans explicitly, since `isinstance(True, int)` is `True` in Python
- Added errors for division by zero and negative square roots

**Tests**
- Expanded from 4 tests to 55 pytest cases and 20 unittest cases
- Added parametrized tests with `@pytest.mark.parametrize`
- Added exception tests using `pytest.raises` and `assertRaises`
- Used additional assertions: `assertAlmostEqual`, `assertIsInstance`,
  `assertNotEqual`, `assertTrue`, `assertFalse`, `assertIn`

**Configuration**
- Added `pytest.ini` for import paths, test discovery, and coverage settings
- Added `__init__.py` to `src/` and `test/`
- Pinned dependency versions in `requirements.txt`

**CI/CD**
- Matrix build across Python 3.11, 3.12 and 3.13
- Coverage gate with `--cov-fail-under=90`; build fails below 90%
- Coverage and test reports uploaded as artifacts
- Added `pull_request` and `workflow_dispatch` triggers
- Added path filters so workflows only run when `lab_1/` changes
- Upgraded to `checkout@v4`, `setup-python@v5`, `upload-artifact@v4`

## Running locally

```bash
cd lab_1
python3 -m venv lab_01
source lab_01/bin/activate
pip install -r requirements.txt

pytest -v
python -m unittest discover -s test -p "test_unittest.py" -v
```

## Functions

| Function | Operation |
|---|---|
| `fun1(x, y)` | Addition |
| `fun2(x, y)` | Subtraction |
| `fun3(x, y)` | Multiplication |
| `fun4(x, y, z)` | Three-way addition |
| `fun5(x, y)` | Division |
| `fun6(x, y)` | Exponentiation |
| `fun7(x)` | Square root |

All raise `ValueError` on invalid input.
