#!/bin/bash

# Simple launcher for AP2-Kite demo
# Ports: 8000(frontend) 8001(ADK) 8002(credentials) 8003(card processor) 8004(auth) 8006(merchant)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../../../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR=".logs"
mkdir -p "$LOG_DIR"

if [ ! -f .env ]; then
  echo ".env not found in repo root: $ROOT_DIR"
  exit 1
fi

# Always use uv's env-file support for every launched process
UV="uv run --package ap2-samples --env-file .env"

cleanup() {
  echo "\nShutting down background processes..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  echo "Cleanup complete."
}
trap cleanup EXIT

echo "Syncing environment..."
uv sync --package ap2-samples >/dev/null

echo "Clearing logs..."
rm -f "$LOG_DIR"/*.log 2>/dev/null || true

PIDS=()

echo "-> ADK Web (8001) ..."
$UV adk web --host 0.0.0.0 --port 8001 --no-reload samples/python/src/roles >"$LOG_DIR/adk_web.log" 2>&1 &
PIDS+=($!)

echo "-> Merchant Agent (8006) ..."
$UV python -m roles.merchant_agent >"$LOG_DIR/merchant_agent.log" 2>&1 &
PIDS+=($!)

echo "-> Credentials Provider (8002) ..."
$UV python -m roles.credentials_provider_agent >"$LOG_DIR/credentials_provider_agent.log" 2>&1 &
PIDS+=($!)

echo "-> Card Processor (8003) ..."
$UV python -m roles.merchant_payment_processor_agent >"$LOG_DIR/mpp_agent.log" 2>&1 &
PIDS+=($!)

echo "-> Auth Server (8004) ..."
$UV python -m roles.shopping_agent.auth_server >"$LOG_DIR/auth_server.log" 2>&1 &
PIDS+=($!)

echo "Waiting 5s for backends..."
sleep 5

echo "-> Frontend (8000) ..."
$UV python -m roles.shopping_agent.simple_frontend >"$LOG_DIR/frontend.log" 2>&1 &
PIDS+=($!)

echo "\nAll services launched"
echo "- Frontend:             http://localhost:8000"
echo "- ADK Web (API):        http://localhost:8001"
echo "- Merchant Agent:       http://localhost:8006"
echo "- Credentials Provider: http://localhost:8002"
echo "- Card Processor:       http://localhost:8003"
echo "- Auth Server:          http://localhost:8004"
echo "Logs in $LOG_DIR/*.log"

wait
