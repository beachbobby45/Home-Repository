#!/bin/bash
# Start the AI Investment Agent dashboard on your Mac.
# Usage: ./scripts/start_dashboard_mac.sh
# Then open: http://127.0.0.1:8080

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"

echo "=== AI Investment Agent Dashboard ==="
echo "Project: $ROOT"
echo ""

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example — add your FINNHUB_API_KEY before trading day refresh."
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
  echo "Installing Python dependencies (first time only)…"
  pip3 install -r "$ROOT/requirements.txt"
fi

echo ""
echo "Starting dashboard at http://127.0.0.1:8080"
echo "Keep this window open. Press Ctrl+C to stop."
echo ""

export PYTHONPATH="$ROOT/src"
exec python3 "$ROOT/scripts/run_dashboard.py" --port 8080
