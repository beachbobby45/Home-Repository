#!/bin/bash
# Hard restart dashboard, wait until healthy, open browser (Mac).
# Usage: ./scripts/hard_restart_dashboard_mac.sh

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
LOG="$ROOT/data/dashboard.log"
PIDFILE="$ROOT/data/dashboard.pid"
URL="http://127.0.0.1:8080"

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

echo "=== Hard restart AI Investment Agent Dashboard ==="
echo "Repo: $ROOT"
echo "Python: $PY ($("$PY" --version 2>&1))"
echo ""

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Pulling latest from origin/main…"
  git -C "$ROOT" pull --ff-only origin main 2>/dev/null || echo "(git pull skipped — update manually if needed)"
  echo ""
fi

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

if ! "$PY" -c "import uvicorn, fastapi, jinja2" 2>/dev/null; then
  echo "Installing dashboard dependencies (one time)…"
fi
"$PY" -m pip install -r "$ROOT/requirements.txt" "pandas>=2.0" "numpy>=1.26"

echo "Checking dashboard loads…"
if ! PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.dashboard.app import app" 2>&1; then
  echo ""
  echo "ERROR: Dashboard code failed to import (see traceback above)."
  echo "Run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  echo "Initializing database…"
  PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()"
fi

export PYTHONPATH="$ROOT/src"
: > "$LOG"
echo "[$(date)] Starting run_dashboard.py on 127.0.0.1:8080" >> "$LOG"

# Start server (background)
nohup "$PY" "$ROOT/scripts/run_dashboard.py" --host 127.0.0.1 --port 8080 >> "$LOG" 2>&1 &
echo $! > "$PIDFILE"
PID=$(cat "$PIDFILE")
echo "Starting dashboard (PID $PID)…"

READY=0
for i in $(seq 1 30); do
  if ! kill -0 "$PID" 2>/dev/null; then
    echo ""
    echo "ERROR: Dashboard process exited before becoming ready."
    echo "--- Log ---"
    tail -50 "$LOG" || true
    echo ""
    echo "Run: ./scripts/doctor_dashboard_mac.sh"
    exit 1
  fi
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/config" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" ]]; then
    READY=1
    break
  fi
  printf "."
  sleep 1
done
echo ""

if [[ "$READY" != "1" ]]; then
  echo "ERROR: Dashboard not responding after 30s (last HTTP $CODE)."
  echo "--- Log ---"
  tail -50 "$LOG" || true
  echo ""
  echo "Run: ./scripts/doctor_dashboard_mac.sh"
  exit 1
fi

echo "Dashboard UP: $URL"
VER=$(curl -s --connect-timeout 2 "$URL/api/version" 2>/dev/null || echo "")
if [[ -n "$VER" ]]; then
  echo "Version: $(echo "$VER" | "$PY" -c "import sys,json; d=json.load(sys.stdin); print(d.get('label','?'))" 2>/dev/null || echo "$VER")"
else
  echo "Version: (could not read /api/version)"
fi
if command -v open >/dev/null 2>&1; then
  open "$URL"
  echo "Opened in your default browser."
else
  echo "Open this URL manually: $URL"
fi
echo "Log: $LOG"
echo "Stop: kill \$(cat $PIDFILE)"
echo ""
echo "If the browser still says 'can't be reached', wait 2s and refresh (Cmd+R)."
exit 0
