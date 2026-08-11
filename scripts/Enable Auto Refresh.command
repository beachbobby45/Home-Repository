#!/bin/bash
# One-time: enable automatic data refresh at 6:30 AM and 4:30 PM (Mac local time).
# Double-click in Finder. No Terminal typing needed after this.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Enable automatic data refresh"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/install_ingest_schedule_mac.sh" ]]; then
  echo "ERROR: install script not found."
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/install_ingest_schedule_mac.sh" 2>/dev/null || true
"$ROOT/scripts/install_ingest_schedule_mac.sh"
STATUS=$?

echo ""
read -r -p "Press Enter to close this window…"
exit $STATUS
