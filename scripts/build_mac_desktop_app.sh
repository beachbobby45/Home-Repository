#!/bin/bash
# Build AI Investment Agent.app and optionally copy to ~/Desktop (Mac).
set -euo pipefail

cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
APP_NAME="AI Investment Agent"
BUNDLE="$ROOT/desktop/${APP_NAME}.app"
INSTALL_DESKTOP=0

for arg in "$@"; do
  case "$arg" in
    --desktop | desktop) INSTALL_DESKTOP=1 ;;
    -h | --help)
      echo "Usage:"
      echo "  ./scripts/build_mac_desktop_app.sh --desktop   # build + copy to ~/Desktop"
      echo "  ./scripts/build_mac_desktop_app.sh             # build only (repo/desktop/)"
      echo ""
      echo "Easier: double-click scripts/Install Desktop App.command in Finder."
      exit 0
      ;;
  esac
done

echo ""
echo "  Building ${APP_NAME}.app"
echo "  Repo: $ROOT"
echo ""

mkdir -p "$BUNDLE/Contents/MacOS" "$BUNDLE/Contents/Resources"

cat > "$BUNDLE/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>launcher</string>
  <key>CFBundleIdentifier</key>
  <string>com.investment-agent.desktop</string>
  <key>CFBundleName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleDisplayName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleVersion</key>
  <string>0.9.0</string>
  <key>CFBundleShortVersionString</key>
  <string>0.9.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>11.0</string>
  <key>NSHighResolutionCapable</key>
  <true/>
  <key>LSUIElement</key>
  <false/>
</dict>
</plist>
EOF

cat > "$BUNDLE/Contents/MacOS/launcher" <<'LAUNCHER'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$DIR/../Resources/repo.path" ]]; then
  ROOT="$(cat "$DIR/../Resources/repo.path" | tr -d '\r\n')"
else
  ROOT="$(cd "$DIR/../../../.." && pwd)"
fi
export INVESTMENT_AGENT_ROOT="$ROOT"
export PYTHONPATH="$ROOT/src"
cd "$ROOT" || exit 1
PY="$(command -v pythonw3 2>/dev/null || command -v python3)"
exec "$PY" "$ROOT/scripts/desktop_helper.py" "$ROOT"
LAUNCHER

chmod +x "$BUNDLE/Contents/MacOS/launcher"
echo "$ROOT" > "$BUNDLE/Contents/Resources/repo.path"

echo "Built in repo: $BUNDLE"
echo "(Finder: Home-Repository → desktop → AI Investment Agent)"
echo ""

if [[ "$INSTALL_DESKTOP" -eq 1 ]]; then
  DESKTOP_DIR="${HOME}/Desktop"
  if [[ ! -d "$DESKTOP_DIR" ]]; then
    echo "ERROR: Desktop folder not found at $DESKTOP_DIR"
    echo "Drag this app manually: $BUNDLE"
    exit 1
  fi
  TARGET="${DESKTOP_DIR}/${APP_NAME}.app"
  rm -rf "$TARGET"
  ditto "$BUNDLE" "$TARGET"
  if [[ ! -d "$TARGET" ]]; then
    echo "ERROR: Copy to Desktop failed."
    exit 1
  fi
  echo "════════════════════════════════════════════════════════"
  echo "  INSTALLED ON DESKTOP"
  echo "  $TARGET"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "In Finder it appears as: AI Investment Agent"
  echo "(no .app suffix shown)"
  echo ""
  echo "First launch: if macOS blocks it, right-click → Open."
  if command -v open >/dev/null 2>&1; then
    open -R "$TARGET"
    echo "Opened Finder and highlighted the app on your Desktop."
  fi
else
  echo "════════════════════════════════════════════════════════"
  echo "  NOT copied to Desktop yet"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "The app is only inside your repo folder right now."
  echo "To put it on your Desktop, run:"
  echo ""
  echo "  cd \"$ROOT\""
  echo "  ./scripts/build_mac_desktop_app.sh --desktop"
  echo ""
  echo "Or double-click in Finder:"
  echo "  Home-Repository/scripts/Install Desktop App.command"
  echo ""
fi

echo ""
