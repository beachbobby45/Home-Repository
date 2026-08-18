#!/bin/bash
# Step 3 — refresh live Finnhub quotes right before you buy or sell in E*TRADE.
# Safe to run with dashboard open (read-only refresh; no full ingest).
#
# Usage: ./scripts/run_refresh_live_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

echo ""
echo "  AI Investment Agent — refresh live (Step 3)"
echo "  Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo ""

"$PY" "$ROOT/scripts/run_refresh_live.py"
