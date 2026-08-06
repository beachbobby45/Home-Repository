#!/bin/bash
# Run full/incremental ingest on Mac while dashboard service is paused (avoids DB lock).
# Usage: ./scripts/run_ingest_mac.sh
#        ./scripts/run_ingest_mac.sh --incremental

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PAUSED=0

cleanup() {
  if [[ "$PAUSED" -eq 1 && -f "$PLIST_PATH" ]]; then
    echo ""
    echo "Restarting dashboard service…"
    launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
    launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
    echo "Dashboard back at http://127.0.0.1:8080"
  fi
}
trap cleanup EXIT

if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "Pausing background dashboard (database unlock for ingest)…"
  launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  sleep 2
  PAUSED=1
fi

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
  sleep 1
fi

echo "Starting ingest…"
export PYTHONPATH="$ROOT/src"
python3 "$ROOT/scripts/run_ingest.py" "$@"

echo ""
echo "Stats:"
python3 "$ROOT/scripts/manage_watchlist.py" stats
