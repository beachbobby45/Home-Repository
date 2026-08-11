#!/bin/bash
# Double-click after market close — refreshes quotes + today's daily bars.
# Use when ranked table / Special Watch look stale same-day.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — After-close ingest"
echo "  Folder: $ROOT"
echo "  Refreshes quotes (2h threshold) and daily bars (12h). ~15–25 min for S&P 500."
echo ""

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_ingest_mac.sh" --after-close
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "After-close ingest finished. Refresh browser → Screen → Run screener."
else
  echo "Ingest exited with code $STATUS — scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
