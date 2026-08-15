#!/bin/bash
# Build AI Investment Agent.app and optionally copy to ~/Desktop (Mac).
set -euo pipefail

cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
APP_NAME="AI Investment Agent"
BUNDLE="$ROOT/desktop/${APP_NAME}.app"
DESKTOP="${1:-}"

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

if [[ "$DESKTOP" == "--desktop" || "$DESKTOP" == "desktop" ]]; then
  TARGET="$HOME/Desktop/${APP_NAME}.app"
  rm -rf "$TARGET"
  ditto "$BUNDLE" "$TARGET"
  echo "Installed on Desktop: $TARGET"
  echo "Double-click it to open — no Terminal needed."
else
  echo "Built: $BUNDLE"
  echo "To copy to Desktop, run:"
  echo "  ./scripts/build_mac_desktop_app.sh --desktop"
fi

echo ""
