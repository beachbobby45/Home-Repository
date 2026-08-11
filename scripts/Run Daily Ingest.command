#!/bin/bash
# Double-click in Finder (Mac) to run daily incremental ingest.
# First time: right-click → Open (macOS may block unknown scripts).
# Takes ~15–25 minutes for a full S&P 500 watchlist — leave this window open.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Daily ingest (incremental)"
echo "  Folder: $ROOT"
echo "  This may take 15–25 minutes. Do not close this window."
echo ""

if [[ ! -f "$ROOT/scripts/run_ingest_mac.sh" ]]; then
  echo "ERROR: Cannot find scripts/run_ingest_mac.sh"
  echo "Make sure Home-Repository is at ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
"$ROOT/scripts/run_ingest_mac.sh" --incremental
STATUS=$?

echo ""
if [[ $STATUS -eq 0 ]]; then
  echo "Daily ingest finished OK. Refresh the dashboard in your browser (Screen tab)."
else
  echo "Ingest exited with code $STATUS. Scroll up for errors."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
