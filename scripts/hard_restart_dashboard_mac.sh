#!/bin/bash
# Hard restart dashboard, wait until healthy, open browser (Mac).
# Usage: ./scripts/hard_restart_dashboard_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
LOG="$ROOT/data/dashboard.log"
PIDFILE="$ROOT/data/dashboard.pid"
URL="http://127.0.0.1:8080"

echo "=== Hard restart AI Investment Agent Dashboard ==="

mkdir -p "$ROOT/data"

stop_pid() {
  if [[ -f "$PIDFILE" ]]; then
    OLD=$(cat "$PIDFILE" 2>/dev/null || true)
    if [[ -n "$OLD" ]] && kill -0 "$OLD" 2>/dev/null; then
      echo "Stopping prior dashboard PID $OLD"
      kill "$OLD" 2>/dev/null || true
      sleep 1
      kill -9 "$OLD" 2>/dev/null || true
    fi
    rm -f "$PIDFILE"
  fi
}

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    echo "Stopping process on port 8080: $PIDS"
    kill $PIDS 2>/dev/null || true
    sleep 1
    PIDS=$(lsof -ti:8080 2>/dev/null || true)
    [[ -n "$PIDS" ]] && kill -9 $PIDS 2>/dev/null || true
  fi
fi
stop_pid

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if ! python3 -c "import uvicorn, fastapi" 2>/dev/null; then
  echo "Installing dependencies…"
  pip3 install -r "$ROOT/requirements.txt"
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  echo "Initializing database…"
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()"
fi

export PYTHONPATH="$ROOT/src"
: > "$LOG"
nohup python3 "$ROOT/scripts/run_dashboard.py" --port 8080 >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
PID=$(cat "$PIDFILE")
echo "Starting dashboard (PID $PID)…"

for i in $(seq 1 25); do
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/config" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" ]]; then
    echo ""
    echo "Dashboard UP: $URL"
    if command -v open >/dev/null 2>&1; then
      open "$URL"
      echo "Opened in your default browser."
    else
      echo "Open this URL in your browser: $URL"
    fi
    echo "Log file: $LOG"
    echo "Stop later: kill \$(cat $PIDFILE)"
    exit 0
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo ""
    echo "ERROR: Dashboard process exited before becoming ready."
    tail -40 "$LOG" || true
    exit 1
  fi
  sleep 1
done

echo ""
echo "ERROR: Dashboard not responding after 25s."
tail -40 "$LOG" || true
exit 1
