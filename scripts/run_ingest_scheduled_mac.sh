#!/bin/bash
# Non-interactive ingest for LaunchAgent schedule (logs to ~/Library/Logs/investment-agent/).
# Usage: ./scripts/run_ingest_scheduled_mac.sh morning|afterclose

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
MODE="${1:-morning}"
LOG_DIR="$HOME/Library/Logs/investment-agent"
LOG_FILE="$LOG_DIR/ingest.log"

mkdir -p "$LOG_DIR"
exec >>"$LOG_FILE" 2>&1

echo ""
echo "======== $(date '+%Y-%m-%d %H:%M:%S %Z') — scheduled ingest ($MODE) ========"

if [[ ! -x "$ROOT/scripts/run_ingest_mac.sh" ]]; then
  chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
fi

case "$MODE" in
  morning)
    "$ROOT/scripts/run_ingest_mac.sh" --incremental
    ;;
  afterclose)
    "$ROOT/scripts/run_ingest_mac.sh" --after-close
    echo "── scheduled screener after ingest ──"
    export PYTHONPATH="$ROOT/src"
    python3 "$ROOT/scripts/run_period_screener.py" --days 14 --save
    python3 "$ROOT/scripts/run_daily_close.py" --daily
    ;;
  *)
    echo "ERROR: unknown mode $MODE (use morning or afterclose)"
    exit 1
    ;;
esac

echo "======== finished $(date '+%Y-%m-%d %H:%M:%S %Z') ========"
