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

chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/fix_ingest_python_mac.sh" 2>/dev/null || true

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

_dashboard_up() {
  curl -sf --connect-timeout 2 "$URL/api/version" >/dev/null 2>&1
}

_start_direct() {
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
  echo "Starting dashboard directly: $PY"
  nohup "$PY" "$ROOT/scripts/run_dashboard.py" --host 127.0.0.1 --port 8080 >>"$LOG" 2>&1 &
  echo $! >"$PIDFILE"
}

if _dashboard_up; then
  echo "Dashboard already running at $URL"
  exit 0
fi

if [[ -f "$PLIST_PATH" ]]; then
  echo "Trying background dashboard service (LaunchAgent)…"
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
  launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 2
fi

if ! _dashboard_up; then
  echo "LaunchAgent did not respond — starting dashboard directly…"
  _start_direct
fi

for _ in $(seq 1 25); do
  if _dashboard_up; then
    echo "Dashboard ready at $URL"
    if command -v open >/dev/null 2>&1; then
      open "$URL"
    fi
    exit 0
  fi
  sleep 1
done

echo "ERROR: Dashboard did not respond at $URL" >&2
echo "Try: ./scripts/fix_ingest_python_mac.sh && ./scripts/install_dashboard_service_mac.sh" >&2
echo "Log: $LOG" >&2
tail -30 "$LOG" 2>/dev/null || true
[[ -f "$HOME/Library/Logs/investment-agent/dashboard.err.log" ]] && \
  tail -20 "$HOME/Library/Logs/investment-agent/dashboard.err.log" >&2 || true
exit 1
