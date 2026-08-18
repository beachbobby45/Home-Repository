#!/bin/bash
# Run full/incremental ingest on Mac while dashboard service is paused (avoids DB lock).
# Usage: ./scripts/run_ingest_mac.sh
#        ./scripts/run_ingest_mac.sh --incremental

set -e
cd "$(dirname "$0")/.." || {
  echo "ERROR: Could not find Home-Repository folder."
  exit 1
}
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

echo ""
echo "  AI Investment Agent — ingest"
echo "  Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo ""

if [[ ! -f "$ROOT/scripts/run_ingest.py" ]]; then
  echo "ERROR: Missing scripts/run_ingest.py — are you in Home-Repository?"
  exit 1
fi

# Clear stale lock from a prior crashed ingest (before preflight / dashboard pause).
CLEARED=$("$PY" -c "from investment_agent.db_maintenance import clear_stale_ingest_lock; print('yes' if clear_stale_ingest_lock() else 'no')")
if [[ "$CLEARED" == "yes" ]]; then
  echo "Cleared stale ingest lock from a prior crashed run."
fi

echo "Preflight (API keys + quick test)…"
if ! "$PY" "$ROOT/scripts/preflight_ingest.py"; then
  echo ""
  echo "Preflight failed — fix the ERROR above, then retry End of Day."
  exit 1
fi
echo ""

PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PAUSED=0

cleanup() {
  local code=$?
  if [[ "$PAUSED" -eq 1 && -f "$PLIST_PATH" ]]; then
    echo ""
    echo "Restarting dashboard service…"
    launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
    launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
    echo "Dashboard back at http://127.0.0.1:8080"
  fi
  if [[ "$code" -ne 0 ]]; then
    echo ""
    if [[ -f "$ROOT/data/ingest_last_error.txt" ]]; then
      cat "$ROOT/data/ingest_last_error.txt"
    elif [[ -f "$ROOT/data/ingest_last_run.json" ]]; then
      "$PY" - "$ROOT/data/ingest_last_run.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text(encoding="utf-8"))
if not data.get("ok") and data.get("errors"):
    print("INGEST FAILED — errors:")
    for err in data["errors"][:8]:
        print(f"  • {err}")
PY
    else
      echo "ERROR: Ingest failed — run: ./scripts/fix_ingest_python_mac.sh"
      echo "       or: ./scripts/doctor_ingest_mac.sh"
    fi
    echo ""
    echo "Ingest failed (exit $code)."
    echo "Dashboard was restarted anyway so the browser works again."
    echo "Tip: ./scripts/fix_ingest_python_mac.sh"
  fi
  exit "$code"
}
trap cleanup EXIT

# macOS default FD limit (~256) is too low for 500+ yfinance requests.
ulimit -n 10240 2>/dev/null || ulimit -n 4096 2>/dev/null || true

# Dedicated yfinance cache — avoids corrupt/default cache and "unable to open database file".
export YFINANCE_CACHE_DIR="$ROOT/data/yfinance_cache"
mkdir -p "$YFINANCE_CACHE_DIR"
export YFINANCE_MIN_INTERVAL_SEC="${YFINANCE_MIN_INTERVAL_SEC:-0.2}"

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

PIDFILE="$ROOT/data/dashboard.pid"
if [[ -f "$PIDFILE" ]]; then
  DPID=$(cat "$PIDFILE" 2>/dev/null || true)
  [[ -n "$DPID" ]] && kill "$DPID" 2>/dev/null || true
  rm -f "$PIDFILE"
fi

echo "Starting ingest…"
"$PY" "$ROOT/scripts/run_ingest.py" "$@"

echo ""
echo "Stats:"
"$PY" "$ROOT/scripts/manage_watchlist.py" stats
