#!/bin/bash
# Fallback if the Desktop .app icon flashes and quits — opens the helper in a window
# with full Terminal PATH so you can see any error messages.
#
# Finder: Home-Repository/scripts/Open Desktop Helper.command

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo ""
echo "  AI Investment Agent — Desktop Helper (window mode)"
echo "  Folder: $ROOT"
echo ""

export PYTHONPATH="$ROOT/src"
export INVESTMENT_AGENT_ROOT="$ROOT"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

chmod +x "$ROOT/scripts/find_desktop_python.sh" "$ROOT/scripts/desktop_helper.py" 2>/dev/null || true

PY="$("$ROOT/scripts/find_desktop_python.sh" 2>/dev/null || true)"
if [[ -z "$PY" ]]; then
  echo "ERROR: No Python with tkinter found."
  echo ""
  echo "Fix (paste in Terminal):"
  echo "  brew install python-tk@3.12"
  echo ""
  read -r -p "Press Enter to close…"
  exit 1
fi

echo "Using: $PY"
echo "Starting window… (leave this Terminal open while using the app)"
echo ""

"$PY" "$ROOT/scripts/desktop_helper.py" "$ROOT"
STATUS=$?

echo ""
if [[ "$STATUS" -eq 0 ]]; then
  echo "Desktop helper closed normally."
else
  echo "Desktop helper exited with code $STATUS."
  echo "Log: ~/.investment_agent/desktop-app.log"
fi
read -r -p "Press Enter to close…"
exit "$STATUS"
