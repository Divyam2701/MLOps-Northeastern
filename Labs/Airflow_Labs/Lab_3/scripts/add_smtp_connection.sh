#!/usr/bin/env bash
# Store Gmail SMTP credentials as the Airflow connection `smtp_default`.
# The password is read from the terminal and saved (encrypted at rest when a
# Fernet key is set) in the Airflow database, never in the repo.
#
# Gmail needs an App Password: https://support.google.com/accounts/answer/185833
set -euo pipefail

AIRFLOW_HOME="${AIRFLOW_HOME:-$HOME/airflow}"
VENV_DIR="${VENV_DIR:-$HOME/airflow_venv}"
set -a; source "$AIRFLOW_HOME/lab3.env"; set +a

read -rp "Gmail address: " SMTP_USER
read -rsp "Gmail App Password (16 characters, input hidden): " SMTP_PASSWORD
echo

"$VENV_DIR/bin/airflow" connections delete smtp_default > /dev/null 2>&1 || true
"$VENV_DIR/bin/airflow" connections add smtp_default \
    --conn-type smtp \
    --conn-host smtp.gmail.com \
    --conn-port 587 \
    --conn-login "$SMTP_USER" \
    --conn-password "$SMTP_PASSWORD" \
    --conn-extra '{"disable_ssl": true, "disable_tls": false}'

echo "Saved. Set the DAG param notify_email (e.g. $SMTP_USER) when you trigger a run."
