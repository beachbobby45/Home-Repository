#!/bin/bash
# Double-click to copy AI_Investment_Agent_PROJECT_PACKAGE.md to Desktop (or Downloads).

cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
SRC="$ROOT/AI_Investment_Agent_PROJECT_PACKAGE.md"
DEST="$HOME/Desktop/AI_Investment_Agent_PROJECT_PACKAGE.md"

if [[ ! -f "$SRC" ]]; then
  echo "Package file not found. Run: git pull origin cursor/patch-investment-agent-spec-cd1d"
  read -r -p "Press Enter to close…"
  exit 1
fi

if [[ ! -d "$HOME/Desktop" ]]; then
  DEST="$HOME/Downloads/AI_Investment_Agent_PROJECT_PACKAGE.md"
fi

cp "$SRC" "$DEST"
echo ""
echo "Copied to:"
echo "  $DEST"
echo ""
ls -lh "$DEST"
echo ""
read -r -p "Press Enter to close…"
