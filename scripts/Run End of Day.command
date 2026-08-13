#!/bin/bash
# Double-click after market close — ingest + screener + daily close report.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — End of day"
echo "  Folder: $ROOT"
echo "  Ingest + screener + close report (~15–30 min for S&P 500)"
echo ""

chmod +x "$ROOT/scripts/run_end_of_day_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_end_of_day_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "End-of-day pipeline finished. Hard-refresh browser (Cmd+Shift+R)."
else
  echo "Pipeline exited with code $STATUS — scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
