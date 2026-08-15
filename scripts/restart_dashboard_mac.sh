#!/bin/bash
# Stop anything on port 8080 and start the dashboard fresh (Mac).
# Usage: ./scripts/restart_dashboard_mac.sh
#
# For background start + auto-open browser, use:
#   ./scripts/hard_restart_dashboard_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"

if [[ "${1:-}" == "--open" ]]; then
  exec "$ROOT/scripts/hard_restart_dashboard_mac.sh"
fi

echo "=== Restart AI Investment Agent Dashboard ==="

# Stop prior dashboard on 8080
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    echo "Stopping old process on port 8080: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 1
    PIDS=$(lsof -ti:8080 2>/dev/null || true)
    [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  fi
fi

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Add FINNHUB_API_KEY and FRED_API_KEY to .env before Refresh live data."
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
  echo "Installing dependencies…"
  pip3 install -r "$ROOT/requirements.txt"
fi

echo ""
echo "Starting dashboard at http://127.0.0.1:8080"
echo "Expected version after restart: v0.9.0 · Phase 1B (check header badge or: curl -s http://127.0.0.1:8080/api/version)"
echo "If you still see 'UI v2': git pull origin main, then run this script again, then Cmd+Shift+R in the browser."
echo "Keep this Terminal window open. Press Ctrl+C to stop."
echo ""

export PYTHONPATH="$ROOT/src"
exec python3 "$ROOT/scripts/run_dashboard.py" --port 8080
