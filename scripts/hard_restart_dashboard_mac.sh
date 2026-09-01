#!/bin/bash
# Hard restart dashboard, wait until healthy, open browser (Mac).
# Uses KeepAlive LaunchAgent so the server survives sleep/reboot/crashes.
# Usage: ./scripts/hard_restart_dashboard_mac.sh
#        ./scripts/hard_restart_dashboard_mac.sh --pull   # git pull origin main first

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
URL="http://127.0.0.1:8080"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"
PIDFILE="$ROOT/data/dashboard.pid"

DO_PULL=0
DO_OPEN=1
for arg in "$@"; do
  case "$arg" in
    --pull) DO_PULL=1 ;;
    --no-open) DO_OPEN=0 ;;
  esac
done

echo "=== Hard restart AI Investment Agent Dashboard ==="
echo "Repo: $ROOT"
echo ""

if [[ "$DO_PULL" -eq 1 ]]; then
  echo "── git pull origin main ──"
  git pull origin main
  echo ""
fi

mkdir -p "$ROOT/data"

# Stop legacy nohup process (older hard_restart versions)
if [[ -f "$PIDFILE" ]]; then
  OLD=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$OLD" ]] && kill -0 "$OLD" 2>/dev/null; then
    echo "Stopping legacy nohup dashboard PID $OLD"
    kill "$OLD" 2>/dev/null || true
    sleep 1
    kill -9 "$OLD" 2>/dev/null || true
  fi
  rm -f "$PIDFILE"
fi

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

if [[ ! -f "$ROOT/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

chmod +x "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true
PYTHON="$("$ROOT/scripts/resolve_python.sh")" || {
  echo ""
  echo "ERROR: No working Python (.venv). Run ./scripts/fix_ingest_python_mac.sh"
  exit 1
}
echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"
echo ""

if ! "$PYTHON" -c "import uvicorn, fastapi, jinja2" 2>/dev/null; then
  echo "Installing dependencies into .venv (this may take a minute)…"
  "$PYTHON" -m pip install -r "$ROOT/requirements.txt"
fi

if ! PYTHONPATH="$ROOT/src" "$PYTHON" -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
  echo ""
  echo "ERROR: Dashboard failed to load. Run ./scripts/doctor_dashboard_mac.sh for details."
  PYTHONPATH="$ROOT/src" "$PYTHON" -c "from investment_agent.dashboard.app import app" 2>&1 | tail -8
  exit 1
fi

if [[ ! -f "$ROOT/data/agent.db" ]]; then
  echo "Initializing database…"
  PYTHONPATH="$ROOT/src" "$PYTHON" -c "from investment_agent.demo_seed import seed_demo_db; seed_demo_db()"
fi

echo "── Installing / restarting KeepAlive dashboard service ──"
echo "(Auto-restarts on crash and on login — no fragile nohup process.)"
echo ""

# install_dashboard_service_mac.sh: writes LaunchAgent plist, bootstrap, kickstart
if ! "$ROOT/scripts/install_dashboard_service_mac.sh"; then
  echo ""
  echo "ERROR: Could not start persistent dashboard service."
  echo "Run: ./scripts/doctor_dashboard_mac.sh"
  echo "Logs: ${LOG_DIR}/dashboard.err.log"
  exit 1
fi

READY=0
CODE="000"
for i in $(seq 1 30); do
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
  echo "--- LaunchAgent stderr ---"
  tail -30 "${LOG_DIR}/dashboard.err.log" 2>/dev/null || true
  echo ""
  echo "Run: ./scripts/doctor_dashboard_mac.sh"
  exit 1
fi

echo "Dashboard UP (KeepAlive service): $URL"
if [[ "$DO_OPEN" -eq 1 ]]; then
  if command -v open >/dev/null 2>&1; then
    open "$URL"
    echo "Opened in your default browser."
  else
    echo "Open this URL manually: $URL"
  fi
else
  echo "(Browser open skipped — caller will open $URL)"
fi
echo ""
echo "Service logs: ${LOG_DIR}/dashboard.out.log"
echo "Status:       ./scripts/dashboard_service_status_mac.sh"
echo "Restart:      launchctl kickstart -k gui/$(id -u)/${PLIST_LABEL}"
echo ""
echo "If the browser shows 'connection failed', wait 2s and Cmd+Shift+R."
exit 0
