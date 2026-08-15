#!/bin/bash
# Double-click this file in Finder (Mac) to update, start the dashboard, and open the browser.
# No Terminal typing — right-click → Open the first time if macOS blocks it.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — open dashboard"
echo "  Folder: $ROOT"
echo ""

if [[ ! -f "$ROOT/scripts/hard_restart_dashboard_mac.sh" ]]; then
  echo "ERROR: Cannot find scripts/hard_restart_dashboard_mac.sh"
  echo "Make sure Home-Repository is cloned to ~/Home-Repository"
  read -r -p "Press Enter to close…"
  exit 1
fi

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Checking for updates on GitHub…"
  git -C "$ROOT" pull --ff-only origin main 2>/dev/null || echo "(Could not auto-update — use Cursor Pull if needed)"
  echo ""
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
else
  echo "Header should show: v0.9.0 · Phase 1B"
  echo "If you still see UI v2, press Cmd+Shift+R in the browser."
fi

read -r -p "Press Enter to close this window…"
exit $STATUS
