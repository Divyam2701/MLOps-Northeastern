"""
### Airflow Lab 3: Ad-click model training pipeline

Daily pipeline on `advertising.csv` that predicts whether a user clicks an ad.

1. **wait_for_data**: sensor that waits until the dataset exists
2. **data**: validate the schema and quality, then split and scale
3. **training**: train every model in the `models` param **in parallel** (dynamic task mapping)
4. **evaluation**: pick the best model, write `metrics.json`, then a **quality gate** branches on `accuracy_threshold`
5. **deploy**: promote the model to `output/production/` and email a report, *or* email a low-accuracy alert

Trigger with **Trigger DAG w/ config** to change the params for one run.
"""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import Param, TriggerRule, dag, task, task_group

from src import model_development as md
from src.notifications import render, send_email, task_failure_alert

default_args = {
    "owner": "Divyam2701",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
    "retry_exponential_backoff": True,   # 30s, 60s, ... up to max_retry_delay
    "max_retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(minutes=10),
    "on_failure_callback": task_failure_alert,
}


@dag(
    dag_id="Airflow_Lab3",
    description="Train, compare and promote ad-click models with a quality gate",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),   # fixed date, not datetime.now()
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    doc_md=__doc__,
    tags=["lab3", "mlops", "classification"],
    params={
        "accuracy_threshold": Param(0.95, type="number", minimum=0, maximum=1,
                                    description="Minimum test accuracy to promote the model"),
        "test_size": Param(0.3, type="number", minimum=0.1, maximum=0.5,
                           description="Fraction of rows held out for testing"),
        "models": Param(list(md.MODELS), type="array",
                        items={"type": "string", "enum": list(md.MODELS)},
                        description="Models to train and compare"),
        "notify_email": Param("", type="string",
                              description="Comma-separated recipients (empty = no email)"),
    },
)
def airflow_lab3():

    @task.sensor(poke_interval=30, timeout=600, mode="reschedule")
    def wait_for_data() -> bool:
        return md.DATA_PATH.exists()

    @task_group(group_id="data")
    def data_group(data_ready):
        @task
        def validate_data() -> dict:
            return md.validate_data()

        @task
        def preprocess(stats: dict, params=None, run_id=None) -> str:
            print(f"Validated dataset: {stats}")
            return md.preprocess(str(md.run_dir(run_id)), test_size=params["test_size"])

        stats = validate_data()
        data_ready >> stats
        return preprocess(stats)

    @task
    def list_models(params=None) -> list[str]:
        return params["models"]

    @task_group(group_id="training")
    def training_group(work_dir: str):
        @task(max_active_tis_per_dagrun=3)
        def train_model(model_name: str, work_dir: str) -> dict:
            result = md.train_model(model_name, work_dir)
            print(f"{model_name}: {result}")
            return result

        return train_model.partial(work_dir=work_dir).expand(model_name=list_models())

    @task_group(group_id="evaluation")
    def evaluation_group(results, work_dir: str):
        @task
        def select_best(results: list[dict], work_dir: str) -> dict:
            return md.select_best(list(results), work_dir)

        @task.branch
        def quality_gate(best: dict, params=None) -> str:
            threshold = params["accuracy_threshold"]
            print(f"Best model {best['model']}: accuracy {best['accuracy']} vs threshold {threshold}")
            if best["accuracy"] >= threshold:
                return "deploy.promote_model"
            return "deploy.alert_low_accuracy"

        best = select_best(results, work_dir)
        return best, quality_gate(best)

    @task_group(group_id="deploy")
    def deploy_group(best: dict, work_dir: str):
        @task
        def promote_model(best: dict, work_dir: str, params=None) -> str:
            return md.promote_model(best, work_dir, params["accuracy_threshold"])

        @task
        def notify_success(best: dict, production_dir: str, work_dir: str,
                           params=None, dag_run=None) -> None:
            html = render("email_report.html", promoted=True, best=best,
                          results=_load_results(work_dir), dag_id=dag_run.dag_id,
                          run_id=dag_run.run_id, threshold=params["accuracy_threshold"],
                          production_dir=production_dir)
            send_email(params["notify_email"],
                       f"[Airflow] {dag_run.dag_id}: {best['model']} promoted "
                       f"(accuracy {best['accuracy']})", html)

        @task
        def alert_low_accuracy(best: dict, work_dir: str, params=None, dag_run=None) -> None:
            html = render("email_report.html", promoted=False, best=best,
                          results=_load_results(work_dir), dag_id=dag_run.dag_id,
                          run_id=dag_run.run_id, threshold=params["accuracy_threshold"])
            send_email(params["notify_email"],
                       f"[Airflow] {dag_run.dag_id}: model below threshold "
                       f"(accuracy {best['accuracy']})", html)

        promoted = promote_model(best, work_dir)
        return promoted, notify_success(best, promoted, work_dir), alert_low_accuracy(best, work_dir)

    done = EmptyOperator(task_id="done", trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)

    work_dir = data_group(wait_for_data())
    results = training_group(work_dir)
    best, gate = evaluation_group(results, work_dir)
    promoted, notified, alerted = deploy_group(best, work_dir)
    gate >> [promoted, alerted]
    [notified, alerted] >> done


def _load_results(work_dir: str) -> list[dict]:
    return json.loads((Path(work_dir) / "metrics.json").read_text())["results"]


airflow_lab3()
