"""ML functions used by the Airflow_Lab3 DAG.

Tasks exchange small JSON-serializable values (file paths and metric dicts)
through XCom instead of pickled DataFrames, which Airflow 3 no longer allows.
Large artifacts (data splits, models) are written to a per-run directory.
"""
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Lab_3/ – everything is resolved relative to the repo, not a hard-coded VM path
LAB_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = Path(os.environ.get("LAB3_DATA_PATH", LAB_DIR / "dags" / "data" / "advertising.csv"))
OUTPUT_DIR = Path(os.environ.get("LAB3_OUTPUT_DIR", LAB_DIR / "output"))
PRODUCTION_DIR = OUTPUT_DIR / "production"

TARGET = "Clicked on Ad"
FEATURES = ["Daily Time Spent on Site", "Age", "Area Income", "Daily Internet Usage", "Male"]
MIN_ROWS = 100

# Candidate models trained in parallel by dynamic task mapping
MODELS = {
    "logistic_regression": lambda: LogisticRegression(max_iter=1000),
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, random_state=42),
    "gradient_boosting": lambda: GradientBoostingClassifier(random_state=42),
}


def run_dir(run_id: str) -> Path:
    """Directory for one DAG run's artifacts (run ids contain ':' and '+')."""
    path = OUTPUT_DIR / "runs" / re.sub(r"[^A-Za-z0-9_.-]", "_", run_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_data(path: Path = DATA_PATH) -> dict:
    """Check the dataset before training; raises ValueError on bad data."""
    data = pd.read_csv(path)

    missing = [c for c in FEATURES + [TARGET] if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if len(data) < MIN_ROWS:
        raise ValueError(f"Only {len(data)} rows, need at least {MIN_ROWS}")
    nulls = data[FEATURES + [TARGET]].isnull().sum()
    if nulls.any():
        raise ValueError(f"Null values found: {nulls[nulls > 0].to_dict()}")
    if set(data[TARGET].unique()) - {0, 1}:
        raise ValueError(f"'{TARGET}' must be binary (0/1)")

    return {
        "rows": int(len(data)),
        "features": FEATURES,
        "positive_rate": round(float(data[TARGET].mean()), 3),
    }


def preprocess(work_dir: str, test_size: float = 0.3, path: Path = DATA_PATH) -> str:
    """Split and scale the data; save the splits and the fitted scaler."""
    data = pd.read_csv(path)
    X, y = data[FEATURES], data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    work_dir = Path(work_dir)
    np.savez(work_dir / "split.npz", X_train=X_train, X_test=X_test,
             y_train=y_train.values, y_test=y_test.values)
    joblib.dump(scaler, work_dir / "scaler.joblib")
    return str(work_dir)


def train_model(model_name: str, work_dir: str) -> dict:
    """Train one candidate model, evaluate it on the test set and save it."""
    work_dir = Path(work_dir)
    split = np.load(work_dir / "split.npz")

    model = MODELS[model_name]()
    model.fit(split["X_train"], split["y_train"])
    predictions = model.predict(split["X_test"])
    y_test = split["y_test"]

    (work_dir / "models").mkdir(exist_ok=True)
    model_path = work_dir / "models" / f"{model_name}.joblib"
    joblib.dump(model, model_path)

    return {
        "model": model_name,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "f1": round(float(f1_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions)), 4),
        "recall": round(float(recall_score(y_test, predictions)), 4),
        "model_path": str(model_path),
    }


def select_best(results: list[dict], work_dir: str) -> dict:
    """Pick the most accurate model (F1 breaks ties) and write metrics.json."""
    results = sorted(results, key=lambda r: (r["accuracy"], r["f1"]), reverse=True)
    best = results[0]

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "best_model": best["model"],
        "results": results,
    }
    (Path(work_dir) / "metrics.json").write_text(json.dumps(report, indent=2))
    return best


def promote_model(best: dict, work_dir: str, threshold: float) -> str:
    """Copy the winning model + scaler to the production folder with a model card."""
    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(best["model_path"], PRODUCTION_DIR / "model.joblib")
    shutil.copy(Path(work_dir) / "scaler.joblib", PRODUCTION_DIR / "scaler.joblib")

    card = {
        "model": best["model"],
        "metrics": {k: best[k] for k in ("accuracy", "f1", "precision", "recall")},
        "accuracy_threshold": threshold,
        "features": FEATURES,
        "source_run": str(work_dir),
        "promoted_at": datetime.now(timezone.utc).isoformat(),
    }
    (PRODUCTION_DIR / "model_card.json").write_text(json.dumps(card, indent=2))
    return str(PRODUCTION_DIR)


if __name__ == "__main__":
    # Run the whole pipeline without Airflow for quick debugging
    print(validate_data())
    work = str(run_dir("local_debug"))
    preprocess(work)
    scores = [train_model(name, work) for name in MODELS]
    best = select_best(scores, work)
    print(json.dumps(best, indent=2))
