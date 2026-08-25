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

chmod +x "$ROOT/scripts/find_desktop_python.sh" 2>/dev/null || true
PY="$("$ROOT/scripts/find_desktop_python.sh" 2>/dev/null || true)"
if [[ -z "$PY" ]]; then
  echo "WARN: No Python with tkinter found at build time."
  echo "      Install: brew install python-tk@3.12"
  echo "      The .app may flash and quit until Python+Tk is fixed."
  PY="$(command -v python3 || echo python3)"
else
  echo "Using Python: $PY"
fi

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
LOG_DIR="$HOME/.investment_agent"
LOG="$LOG_DIR/desktop-app.log"
mkdir -p "$LOG_DIR"

alert() {
  /usr/bin/osascript -e "display alert \"AI Investment Agent\" message \"$1\" as critical" 2>/dev/null || true
}

{
  echo ""
  echo "=== launch $(date) ==="
  DIR="$(cd "$(dirname "$0")" && pwd)"
  ROOT=""

  if [[ -f "$DIR/../Resources/repo.path" ]]; then
    ROOT="$(tr -d '\r\n' < "$DIR/../Resources/repo.path")"
    echo "repo.path: $ROOT"
  fi
  if [[ -z "$ROOT" || ! -f "$ROOT/scripts/run_dashboard.py" ]]; then
    if [[ -f "$HOME/.investment_agent/repo.path" ]]; then
      ROOT="$(tr -d '\r\n' < "$HOME/.investment_agent/repo.path")"
      echo "config repo.path: $ROOT"
    fi
  fi
  if [[ -z "$ROOT" || ! -f "$ROOT/scripts/run_dashboard.py" ]]; then
    echo "ERROR: Home-Repository not found"
    alert "Could not find Home-Repository. Reinstall from scripts/Install Desktop App.command"
    exit 1
  fi

  export INVESTMENT_AGENT_ROOT="$ROOT"
  export PYTHONPATH="$ROOT/src"
  export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
  cd "$ROOT" || exit 1

  PY=""
  if [[ -f "$DIR/../Resources/python.path" ]]; then
    PY="$(tr -d '\r\n' < "$DIR/../Resources/python.path")"
    if [[ -n "$PY" && -x "$PY" ]] && "$PY" -c "import tkinter" 2>/dev/null; then
      echo "python.path: $PY"
    else
      echo "WARN: pinned python.path invalid: $PY"
      PY=""
    fi
  fi
  if [[ -z "$PY" ]]; then
    for candidate in \
      /opt/homebrew/bin/pythonw /opt/homebrew/bin/python3 \
      /usr/local/bin/pythonw /usr/local/bin/python3 \
      /usr/bin/pythonw \
      /Library/Frameworks/Python.framework/Versions/3.12/bin/pythonw \
      /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
      pythonw3 pythonw python3
    do
      if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
        cmd="$candidate"
        [[ -x "$candidate" ]] || cmd="$(command -v "$candidate")"
        if "$cmd" -c "import tkinter" 2>/dev/null; then
          PY="$cmd"
          echo "python (search): $PY"
          break
        fi
      fi
    done
  fi

  if [[ -z "$PY" ]]; then
    echo "ERROR: no Python with tkinter"
    alert "Python with Tkinter not found. In Terminal run: brew install python-tk@3.12"
    exit 1
  fi

  "$PY" "$ROOT/scripts/desktop_helper.py" "$ROOT"
  CODE=$?
  echo "exit code: $CODE"
  if [[ "$CODE" -ne 0 ]]; then
    alert "App exited with an error. See ~/.investment_agent/desktop-app.log"
  fi
  exit "$CODE"
} >> "$LOG" 2>&1
LAUNCHER

chmod +x "$BUNDLE/Contents/MacOS/launcher"
echo "$ROOT" > "$BUNDLE/Contents/Resources/repo.path"
echo "$PY" > "$BUNDLE/Contents/Resources/python.path"

echo "Built in repo: $BUNDLE"
echo "Python pinned: $PY"
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
  xattr -cr "$TARGET" 2>/dev/null || true
  echo "Cleared quarantine flags (xattr) on Desktop copy."
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
