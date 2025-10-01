#!/bin/bash

# One-shot launcher for AP2-Kite demo with custom frontend + ADK + auth
# Ports: 8000 (frontend), 8001 (ADK), 8004 (auth)

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

UV_RUN_CMD="uv run --no-sync --package ap2-samples"
if [ -f .env ]; then
  UV_RUN_CMD="$UV_RUN_CMD --env-file .env"
fi

echo "Clearing logs..."
rm -f "$LOG_DIR"/* || true

pids=()

echo "-> Starting ADK Web (port:8001) ..."
$UV_RUN_CMD adk web --host 0.0.0.0 --port 8001 samples/python/src/roles >"$LOG_DIR/adk_web.log" 2>&1 &
pids+=($!)

echo "-> Starting Kite Authentication Server (port:8004) ..."
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
echo "- Kite Auth Server:   http://localhost:8004"
echo "\nLogs: .logs/{frontend,adk_web,auth_server}.log"
echo "Press Ctrl+C to stop."

# Keep script running to maintain trap/cleanup
wait


