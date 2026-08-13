#!/bin/bash
# Double-click right before you place a limit buy or sell in E*TRADE (Step 3).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Refresh live before buy/sell"
echo "  Folder: $ROOT"
echo ""

chmod +x "$ROOT/scripts/run_refresh_live_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_refresh_live_mac.sh"
STATUS=$?

echo ""
read -r -p "Press Enter to close this window…"
exit $STATUS
