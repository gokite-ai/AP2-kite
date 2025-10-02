#!/bin/bash

# One-shot launcher for AP2-Kite demo with custom frontend + ADK + auth
# Ports: 8000 (frontend), 8001 (ADK), 8002 (credentials), 8003 (card processor), 8004 (auth), 8006 (merchant)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR=".logs"
mkdir -p "$LOG_DIR"

cleanup() {
  echo "\nShutting down background processes..."
  for pid in "${pids[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  echo "Cleanup complete."
}
trap cleanup EXIT

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

echo "Syncing virtual environment with uv sync..."
if uv sync --package ap2-samples; then
  echo "Virtual environment synced successfully."
else
  echo "Error: uv sync failed. Aborting."
  exit 1
fi

UV_RUN_CMD="uv run --package ap2-samples"
if [ -f .env ]; then
  UV_RUN_CMD="$UV_RUN_CMD --env-file .env"
fi

echo "Clearing logs..."
rm -f "$LOG_DIR"/* || true

pids=()

echo "-> Starting the ADK Web Interface (port:8001 log:$LOG_DIR/adk_web.log)..."
$UV_RUN_CMD adk web --host 0.0.0.0 --port 8001 samples/python/src/roles >"$LOG_DIR/adk_web.log" 2>&1 &
pids+=($!)

echo "-> Starting the Merchant Agent (port:8006 log:$LOG_DIR/merchant_agent.log)..."
$UV_RUN_CMD python -m roles.merchant_agent >"$LOG_DIR/merchant_agent.log" 2>&1 &
pids+=($!)

echo "-> Starting the Credentials Provider (port:8002 log:$LOG_DIR/credentials_provider_agent.log)..."
$UV_RUN_CMD python -m roles.credentials_provider_agent >"$LOG_DIR/credentials_provider_agent.log" 2>&1 &
pids+=($!)

echo "-> Starting the Card Processor Agent (port:8003 log:$LOG_DIR/mpp_agent.log)..."
$UV_RUN_CMD python -m roles.merchant_payment_processor_agent >"$LOG_DIR/mpp_agent.log" 2>&1 &
pids+=($!)

echo "-> Starting the Kite Authentication Server (port:8004 log:$LOG_DIR/auth_server.log)..."
$UV_RUN_CMD python -m roles.shopping_agent.auth_server >"$LOG_DIR/auth_server.log" 2>&1 &
pids+=($!)

echo "Waiting 5s for backends to warm up..."
sleep 5

echo "-> Starting Custom Frontend (port:8000) ..."
$UV_RUN_CMD python -m roles.shopping_agent.simple_frontend >"$LOG_DIR/frontend.log" 2>&1 &
pids+=($!)

echo "\nAll services launched:"
echo "- Frontend:           http://localhost:8000"
echo "- ADK Web (API):      http://localhost:8001"
echo "- Merchant Agent:     http://localhost:8006"
echo "- Credentials Provider: http://localhost:8002"
echo "- Card Processor:     http://localhost:8003"
echo "- Kite Auth Server:   http://localhost:8004"
echo "\nLogs: .logs/{frontend,merchant_agent,credentials_provider_agent,mpp_agent,auth_server,adk_web}.log"
echo "Press Ctrl+C to stop."

# Keep script running to maintain trap/cleanup
wait


