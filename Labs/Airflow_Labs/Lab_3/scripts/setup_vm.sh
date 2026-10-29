#!/usr/bin/env bash
# One-shot setup of Airflow 3 for Lab 3 on an Ubuntu/Debian VM.
#
#   git clone <your repo> && cd <repo>/Labs/Airflow_Labs/Lab_3
#   bash scripts/setup_vm.sh
#
# Installs Airflow in a virtualenv (pinned with the official constraints file),
# points it at this lab's dags/ folder, and runs each Airflow component as a
# systemd service so it restarts on failure and starts on boot.
set -euo pipefail

AIRFLOW_VERSION="${AIRFLOW_VERSION:-3.3.2}"
AIRFLOW_PORT="${AIRFLOW_PORT:-8080}"
AIRFLOW_HOME="${AIRFLOW_HOME:-$HOME/airflow}"
VENV_DIR="${VENV_DIR:-$HOME/airflow_venv}"
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$AIRFLOW_HOME/lab3.env"
SERVICES=(api-server scheduler dag-processor triggerer)

echo "==> Installing system packages"
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip openssl curl

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
CONSTRAINTS="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PY_VERSION}.txt"

echo "==> Creating virtualenv $VENV_DIR (Python $PY_VERSION)"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install "apache-airflow==${AIRFLOW_VERSION}" \
    -r "$LAB_DIR/requirements.txt" --constraint "$CONSTRAINTS"

echo "==> Writing $ENV_FILE"
mkdir -p "$AIRFLOW_HOME" "$LAB_DIR/output"
if [[ ! -f "$ENV_FILE" ]]; then
    # Secrets are generated once and shared by all components (Airflow 3 needs
    # the same JWT secret in the api-server and the scheduler/workers)
    cat > "$ENV_FILE" <<EOF
AIRFLOW_HOME=$AIRFLOW_HOME
AIRFLOW__CORE__DAGS_FOLDER=$LAB_DIR/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://localhost:$AIRFLOW_PORT/execution/
AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_USERS=admin:admin
AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE=$AIRFLOW_HOME/passwords.json
AIRFLOW__API__HOST=0.0.0.0
AIRFLOW__API__PORT=$AIRFLOW_PORT
AIRFLOW__API__SECRET_KEY=$(openssl rand -hex 32)
AIRFLOW__API_AUTH__JWT_SECRET=$(openssl rand -hex 32)
LAB3_OUTPUT_DIR=$LAB_DIR/output
EOF
    chmod 600 "$ENV_FILE"
fi

if [[ ! -f "$AIRFLOW_HOME/passwords.json" ]]; then
    echo "{\"admin\": \"$(openssl rand -base64 12 | tr -d '/+=')\"}" > "$AIRFLOW_HOME/passwords.json"
    chmod 600 "$AIRFLOW_HOME/passwords.json"
fi

echo "==> Initialising the Airflow database"
set -a; source "$ENV_FILE"; set +a
"$VENV_DIR/bin/airflow" db migrate

echo "==> Installing systemd services"
for svc in "${SERVICES[@]}"; do
    sudo tee "/etc/systemd/system/airflow-$svc.service" > /dev/null <<EOF
[Unit]
Description=Airflow $svc (Lab 3)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
EnvironmentFile=$ENV_FILE
WorkingDirectory=$AIRFLOW_HOME
ExecStart=$VENV_DIR/bin/airflow $svc
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
done
sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICES[@]/#/airflow-}"

echo "==> Waiting for the API server"
for _ in $(seq 1 60); do
    curl -sf "http://localhost:$AIRFLOW_PORT/api/v2/monitor/health" > /dev/null && break
    sleep 3
done

EXTERNAL_IP="$(curl -sf -H 'Metadata-Flavor: Google' \
    http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip \
    || hostname -I | awk '{print $1}')"

cat <<EOF

Airflow is running.
  UI:        http://$EXTERNAL_IP:$AIRFLOW_PORT   (open port $AIRFLOW_PORT in the VM firewall)
  Login:     admin / $(python3 -c "import json; print(json.load(open('$AIRFLOW_HOME/passwords.json'))['admin'])")
  Status:    sudo systemctl status 'airflow-*'
  Logs:      journalctl -u airflow-scheduler -f

Optional, for email notifications:
  bash scripts/add_smtp_connection.sh
EOF
