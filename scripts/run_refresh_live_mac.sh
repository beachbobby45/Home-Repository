#!/bin/bash
# Step 3 — refresh live Finnhub quotes right before you buy or sell in E*TRADE.
# Safe to run with dashboard open (read-only refresh; no full ingest).
#
# Usage: ./scripts/run_refresh_live_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — refresh live (Step 3)"
echo "  Folder: $ROOT"
echo ""

export PYTHONPATH="$ROOT/src"
python3 "$ROOT/scripts/run_refresh_live.py"
