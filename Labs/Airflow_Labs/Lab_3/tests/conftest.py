import os
import sys
from pathlib import Path

os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")

# Make `src` importable the same way Airflow does (dags/ is on sys.path)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dags"))
