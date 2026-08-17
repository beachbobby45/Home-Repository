#!/bin/bash
# Double-click once to put AI Investment Agent.app on your Desktop (Mac).
# The app has buttons for Update, Morning Prep, Refresh Live, End of Day — no Terminal.

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  Installing AI Investment Agent on your Desktop…"
echo "  Folder: $ROOT"
echo ""

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer is for Mac only."
  read -r -p "Press Enter to close…"
  exit 1
fi

chmod +x "$ROOT/scripts/build_mac_desktop_app.sh" "$ROOT/scripts/desktop_helper.py" 2>/dev/null || true
"$ROOT/scripts/build_mac_desktop_app.sh" --desktop

echo ""
echo "Done. Look on your Desktop for: AI Investment Agent"
echo "(Finder hides the .app — it is not a folder you open in Terminal.)"
echo "Double-click it. First time: right-click → Open if macOS asks."
echo ""
echo "If the .app icon flashes and disappears, use this fallback instead:"
echo "  Home-Repository/scripts/Open Desktop Helper.command"
echo ""
echo "Or run the doctor in Terminal:"
echo "  cd \"$ROOT\" && ./scripts/doctor_desktop_app_mac.sh"
echo "Log file: ~/.investment_agent/desktop-app.log"
echo ""
read -r -p "Press Enter to close…"
