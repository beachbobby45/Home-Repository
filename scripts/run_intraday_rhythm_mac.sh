#!/bin/bash
# Intraday rhythm — scheduled refresh + quote snapshots (Mac, ET session).
#
# Modes (pass as first argument):
#   morning_prep  — screener + candidates + pre_market snapshot (≈7:00 ET)
#   at_open       — live refresh + at_open snapshot (≈9:31 ET)
#   opening_drive — live refresh for Opening Drive window (≈9:36 / 9:41 ET)
#   plus_15m      — live refresh + plus_15m snapshot (≈9:46 ET)
#   trade_refresh — periodic Step 3 refresh (10:00–14:30 ET)
#
# Usage:
#   ./scripts/run_intraday_rhythm_mac.sh morning_prep
#   ./scripts/run_intraday_rhythm_mac.sh at_open

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

MODE="${1:-trade_refresh}"
LOG_DIR="${HOME}/Library/Logs/investment-agent"
mkdir -p "$LOG_DIR"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo "  AI Investment Agent — intraday rhythm ($MODE)"
echo "  $STAMP · Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo ""

_run_refresh() {
  PYTHONNOUSERSITE=1 "$PY" "$ROOT/scripts/run_refresh_live.py" --json
}

_run_snapshot() {
  local slot="$1"
  PYTHONNOUSERSITE=1 "$PY" "$ROOT/scripts/run_quote_snapshots.py" --slot "$slot" --json
}

case "$MODE" in
  morning_prep)
    chmod +x "$ROOT/scripts/run_morning_prep_mac.sh" 2>/dev/null || true
    "$ROOT/scripts/run_morning_prep_mac.sh" --with-ingest
    _run_snapshot pre_market || true
    ;;
  at_open)
    _run_refresh
    _run_snapshot at_open
    ;;
  opening_drive)
    _run_refresh
    ;;
  plus_15m)
    _run_refresh
    _run_snapshot plus_15m
    ;;
  trade_refresh)
    _run_refresh
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Use: morning_prep | at_open | opening_drive | plus_15m | trade_refresh"
    exit 1
    ;;
esac

echo ""
echo "Intraday rhythm complete ($MODE)."
echo ""
