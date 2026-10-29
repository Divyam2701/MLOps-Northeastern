#!/usr/bin/env bash
# Trigger Airflow_Lab3 remotely through the Airflow 3 REST API (v2).
#
#   AIRFLOW_PASSWORD=... bash scripts/trigger_dag.sh http://<VM-IP>:8080 '{"accuracy_threshold": 0.97}'
#
# Airflow 3 uses JWT auth: exchange username/password for a token at
# /auth/token, then call /api/v2 with "Authorization: Bearer <token>".
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
CONF="${2:-}"
[[ -n "$CONF" ]] || CONF='{}'
DAG_ID="${DAG_ID:-Airflow_Lab3}"
AIRFLOW_USER="${AIRFLOW_USER:-admin}"
: "${AIRFLOW_PASSWORD:?Set AIRFLOW_PASSWORD (printed by setup_vm.sh)}"

TOKEN="$(curl -sf -X POST "$BASE_URL/auth/token" \
    -H 'Content-Type: application/json' \
    -d "{\"username\": \"$AIRFLOW_USER\", \"password\": \"$AIRFLOW_PASSWORD\"}" \
    | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')"

# New DAGs start paused; unpause so the run is picked up by the scheduler
curl -sf -X PATCH "$BASE_URL/api/v2/dags/$DAG_ID" \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d '{"is_paused": false}' > /dev/null

curl -sf -X POST "$BASE_URL/api/v2/dags/$DAG_ID/dagRuns" \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "{\"logical_date\": null, \"conf\": $CONF}" \
    | python3 -c 'import sys, json; r = json.load(sys.stdin); print("Triggered %s: run_id=%s state=%s" % (r["dag_id"], r["dag_run_id"], r["state"]))'
