#!/bin/bash
# Double-click in Finder to download the latest code and restart the dashboard.
# No typing in Terminal — a window opens, runs the update, opens the browser, then waits for Enter.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Update and open dashboard"
echo "  Folder: $ROOT"
echo ""
echo "  This will:"
echo "    1. Download the latest version from GitHub"
echo "    2. Restart the dashboard"
echo "    3. Open http://127.0.0.1:8080 in your browser"
echo ""
  echo "  Look for v0.9.1 · \$15K · Annual Sweep in the top-left header."
  echo "  Status bar should show Cash \$15,000 and Today … / \$200."
echo ""

if [[ ! -f "$ROOT/scripts/hard_restart_dashboard_mac.sh" ]]; then
  echo "ERROR: Cannot find the dashboard scripts."
  echo "Make sure Home-Repository is cloned to ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/hard_restart_dashboard_mac.sh" "$ROOT/scripts/doctor_dashboard_mac.sh" 2>/dev/null || true
"$ROOT/scripts/hard_restart_dashboard_mac.sh"
STATUS=$?

echo ""
if [[ $STATUS -ne 0 ]]; then
  echo "Update or start failed. Running doctor…"
  "$ROOT/scripts/doctor_dashboard_mac.sh" || true
  echo ""
  echo "Copy the text above and send it for help."
else
  echo "Done. In the browser header you should see: v0.9.1 · \$15K · Annual Sweep"
  echo "Cash should read \$15,000 and daily target \$200/day (empty journal)."
  echo "If the old label still shows, press Cmd+Shift+R to hard-refresh."
fi

echo ""
read -r -p "Press Enter to close this window…"
exit $STATUS
