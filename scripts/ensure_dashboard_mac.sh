#!/bin/bash
# Start or restart the dashboard on 127.0.0.1:8080 using project .venv Python.
# Usage: ./scripts/ensure_dashboard_mac.sh
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
URL="http://127.0.0.1:8080"
LOG="$ROOT/data/dashboard.log"
PIDFILE="$ROOT/data/dashboard.pid"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

if curl -sf --connect-timeout 2 "$URL/api/version" >/dev/null 2>&1; then
  echo "Dashboard already running at $URL"
  exit 0
fi

echo "Starting dashboard with $PY …"

if [[ -f "$PLIST_PATH" ]]; then
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
  launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
else
  if command -v lsof >/dev/null 2>&1; then
    PIDS=$(lsof -ti:8080 2>/dev/null || true)
    [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
    sleep 1
  fi
  if [[ -f "$PIDFILE" ]]; then
    OLD=$(cat "$PIDFILE" 2>/dev/null || true)
    [[ -n "$OLD" ]] && kill "$OLD" 2>/dev/null || true
    rm -f "$PIDFILE"
  fi
  mkdir -p "$ROOT/data"
  export PYTHONPATH="$ROOT/src"
  nohup "$PY" "$ROOT/scripts/run_dashboard.py" --host 127.0.0.1 --port 8080 >>"$LOG" 2>&1 &
  echo $! >"$PIDFILE"
fi

for _ in $(seq 1 25); do
  if curl -sf --connect-timeout 2 "$URL/api/version" >/dev/null 2>&1; then
    echo "Dashboard ready at $URL"
    exit 0
  fi
  sleep 1
done

echo "ERROR: Dashboard did not respond at $URL" >&2
echo "Run: ./scripts/doctor_dashboard_mac.sh" >&2
echo "Log: $LOG" >&2
[[ -f "$HOME/Library/Logs/investment-agent/dashboard.err.log" ]] && \
  tail -20 "$HOME/Library/Logs/investment-agent/dashboard.err.log" >&2 || true
exit 1
