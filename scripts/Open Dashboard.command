#!/bin/bash
# Double-click this file in Finder (Mac) to start the dashboard and open the browser.
# First time: right-click → Open (macOS may block unknown scripts).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — starting dashboard"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/hard_restart_dashboard_mac.sh" ]]; then
  echo "ERROR: Cannot find scripts/hard_restart_dashboard_mac.sh"
  echo "Make sure Home-Repository is cloned to ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/hard_restart_dashboard_mac.sh" "$ROOT/scripts/doctor_dashboard_mac.sh" 2>/dev/null || true
"$ROOT/scripts/hard_restart_dashboard_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -ne 0 ]]; then
  echo "Start failed. Running doctor…"
  "$ROOT/scripts/doctor_dashboard_mac.sh" || true
  echo ""
  echo "Copy the output above and send it for help."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
