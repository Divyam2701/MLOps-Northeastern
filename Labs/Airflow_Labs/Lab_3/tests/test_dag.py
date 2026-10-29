"""DAG integrity tests: the DAG loads and the pipeline is wired as intended."""
from pathlib import Path

import pytest
from airflow.dag_processing.dagbag import DagBag

DAGS_DIR = Path(__file__).resolve().parents[1] / "dags"


@pytest.fixture(scope="module")
def dag():
    bag = DagBag(dag_folder=str(DAGS_DIR))
    assert bag.import_errors == {}, f"Import errors: {bag.import_errors}"
    return bag.get_dag("Airflow_Lab3")


def test_dag_loaded(dag):
    assert dag is not None
    assert not dag.catchup
    assert dag.max_active_runs == 1


def test_expected_tasks(dag):
    assert set(dag.task_ids) == {
        "wait_for_data",
        "data.validate_data", "data.preprocess",
        "training.list_models", "training.train_model",
        "evaluation.select_best", "evaluation.quality_gate",
        "deploy.promote_model", "deploy.notify_success", "deploy.alert_low_accuracy",
        "done",
    }


def test_quality_gate_branches(dag):
    gate = dag.get_task("evaluation.quality_gate")
    assert gate.downstream_task_ids == {"deploy.promote_model", "deploy.alert_low_accuracy"}


def test_pipeline_order(dag):
    assert "data.validate_data" in dag.get_task("wait_for_data").downstream_task_ids
    assert "training.train_model" in dag.get_task("data.preprocess").downstream_task_ids
    assert "evaluation.select_best" in dag.get_task("training.train_model").downstream_task_ids


def test_default_args(dag):
    task = dag.get_task("data.preprocess")
    assert task.retries == 2
    assert task.retry_exponential_backoff
    assert task.execution_timeout is not None
    assert task.on_failure_callback
