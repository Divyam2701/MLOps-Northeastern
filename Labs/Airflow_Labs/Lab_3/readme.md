# Airflow Lab 3: ML Pipeline on a Cloud VM (Airflow 3)

An Airflow 3 DAG on a cloud VM that trains three ad-click models in parallel, promotes the best
one only if it passes an accuracy check, and emails a report.

## Pipeline

```
wait_for_data ─► validate_data ─► preprocess ─► train_model ×3 (parallel) ─► select_best ─► quality_gate
                                                                                              │
                                              accuracy ≥ threshold ─► promote_model ─► notify_success
                                              accuracy < threshold ─► alert_low_accuracy
```

## Key Changes (vs. original lab)

| # | Change | Why |
|---|--------|-----|
| 1 | **Rewritten for Airflow 3** with the TaskFlow API (`@dag`, `@task`, `@task_group`) | The original used Airflow 2 code that fails on Airflow 3. |
| 2 | **3 models trained in parallel** (Logistic Regression, Random Forest, Gradient Boosting) with **dynamic task mapping** | The original trained one model and never evaluated it. |
| 3 | **Quality gate** (`@task.branch`): the best model is promoted only if accuracy ≥ `accuracy_threshold`, otherwise an alert is sent | Only good models reach "production". |
| 4 | **Sensor + data validation** before training | The pipeline waits for the data and stops early on bad data. |
| 5 | **Retries with backoff, timeouts and a failure-alert email** on every task | Recovers from temporary errors and reports real failures. |
| 6 | **Run-time params** (`accuracy_threshold`, `test_size`, `models`, `notify_email`) | Runs are configured from the UI or API without editing code. |
| 7 | **One-command VM deployment** (`scripts/setup_vm.sh`) that runs Airflow as **4 systemd services** | Replaces the manual setup; the services restart on failure and survive reboots. |
| 8 | **REST API trigger** (`scripts/trigger_dag.sh`) using Airflow 3's `/api/v2` with JWT auth | The original API setup no longer exists in Airflow 3. |
| 9 | **Email fixed**: uses an Airflow SMTP connection and an HTML report | The original had a placeholder recipient and crashed on errors. |
| 10 | **12 pytest tests** for the DAG and the ML code | Catches broken DAGs before deploying. |

## How to Run

On an Ubuntu 24.04 VM with TCP port 8080 open:
```bash
git clone https://github.com/Divyam2701/MLOps.git
cd MLOps/Labs/Airflow_Labs/Lab_3
bash scripts/setup_vm.sh                 # prints the UI address and admin password
bash scripts/add_smtp_connection.sh      # optional: Gmail App Password for emails
```
Open `http://<VM-IP>:8080`, then unpause and trigger `Airflow_Lab3`. Set `accuracy_threshold`
to `0.99` to see the alert branch.

## Results

| Model | Accuracy | F1 |
|-------|----------|----|
| **logistic_regression** (promoted) | **0.9767** | 0.9764 |
| random_forest | 0.9700 | 0.9701 |
| gradient_boosting | 0.9600 | 0.9603 |

## Screenshots

<!-- Add screenshots from the VM run here -->
