#!/bin/bash
# Double-click before open — screener + trade candidates (Step 2).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Morning prep"
echo "  Folder: $ROOT"
echo ""

chmod +x "$ROOT/scripts/run_morning_prep_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_morning_prep_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "Morning prep done. Before buying: double-click Run Refresh Live.command"
else
  echo "Morning prep exited with code $STATUS."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
