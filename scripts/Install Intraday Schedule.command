#!/bin/bash
# One-time install: morning + opening-window LaunchAgents (7:00, 9:31, 9:36, … ET).
# Double-click in Finder — no Terminal typing required.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — install intraday schedule"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/install_intraday_schedule_mac.sh" ]]; then
  echo "ERROR: install_intraday_schedule_mac.sh not found."
  echo ""
  echo "This feature is on branch cursor/opening-drive-automation-cd1d (PR #21)."
  echo "Merge PR #21 on GitHub, then run Update and Open Dashboard.command,"
  echo "or ask your agent to merge the PR, then pull main again."
  echo ""
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/install_intraday_schedule_mac.sh" 2>/dev/null || true
"$ROOT/scripts/install_intraday_schedule_mac.sh"
STATUS=$?

echo ""
read -r -p "Press Enter to close…"
exit $STATUS
