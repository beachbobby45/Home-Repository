#!/bin/bash
# Double-click this file in Finder to copy the project package to your Desktop.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/AI_Investment_Agent_PROJECT_PACKAGE.md"

if [[ ! -f "$SRC" ]]; then
  osascript -e 'display alert "File not found" message "Run git pull in Home-Repository first, then double-click again."'
  exit 1
fi

DESKTOP="$HOME/Desktop"
if [[ ! -d "$DESKTOP" ]]; then
  DESKTOP="$HOME/Downloads"
  mkdir -p "$DESKTOP"
fi

DEST="$DESKTOP/AI_Investment_Agent_PROJECT_PACKAGE.md"
cp "$SRC" "$DEST"

open -R "$DEST"

osascript -e "display notification \"Copied to Desktop\" with title \"AI Investment Agent\""

echo "Done: $DEST"
read -r -p "Press Enter to close…"
