"""Unit tests for the ML functions, run on the real dataset."""
import json

import pandas as pd
import pytest

from src import model_development as md


@pytest.fixture
def work_dir(tmp_path):
    return str(md.preprocess(str(tmp_path), test_size=0.3))


def test_validate_data_ok():
    stats = md.validate_data()
    assert stats["rows"] == 1000
    assert 0 < stats["positive_rate"] < 1


def test_validate_data_rejects_missing_column(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.read_csv(md.DATA_PATH).drop(columns=["Age"]).to_csv(bad, index=False)
    with pytest.raises(ValueError, match="Missing columns"):
        md.validate_data(bad)


def test_validate_data_rejects_nulls(tmp_path):
    bad = tmp_path / "bad.csv"
    data = pd.read_csv(md.DATA_PATH)
    data.loc[0, "Age"] = None
    data.to_csv(bad, index=False)
    with pytest.raises(ValueError, match="Null values"):
        md.validate_data(bad)


@pytest.mark.parametrize("model_name", list(md.MODELS))
def test_train_model(work_dir, model_name):
    result = md.train_model(model_name, work_dir)
    assert result["model"] == model_name
    assert result["accuracy"] > 0.9


def test_select_best_writes_report(work_dir):
    results = [md.train_model(name, work_dir) for name in md.MODELS]
    best = md.select_best(results, work_dir)
    report = json.loads((md.Path(work_dir) / "metrics.json").read_text())
    assert best["accuracy"] == max(r["accuracy"] for r in results)
    assert report["best_model"] == best["model"]
