#!/bin/bash
# Double-click this file in Finder to copy the Siena Loop valuation PDF to your Desktop.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/real_estate/13994-Siena-Loop-valuation.pdf"

if [[ ! -f "$SRC" ]]; then
  osascript -e 'display alert "File not found" message "Run git pull in Home-Repository first, then double-click again."'
  exit 1
fi

DESKTOP="$HOME/Desktop"
if [[ ! -d "$DESKTOP" ]]; then
  DESKTOP="$HOME/Downloads"
  mkdir -p "$DESKTOP"
fi

DEST="$DESKTOP/13994 Siena Loop - Lakewood Ranch valuation.pdf"
cp "$SRC" "$DEST"

if command -v open >/dev/null 2>&1; then
  open -R "$DEST" || true
fi

osascript -e "display notification \"Copied to Desktop\" with title \"Siena Loop valuation\"" || true

echo "Done: $DEST"
read -r -p "Press Enter to close…"
