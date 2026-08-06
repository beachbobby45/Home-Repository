#!/bin/bash
# Install macOS LaunchAgent — dashboard runs in background (no Terminal window).
# Usage: ./scripts/install_dashboard_service_mac.sh
# Open: http://127.0.0.1:8080

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
PYTHON="$(command -v python3)"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"

if [[ -z "$PYTHON" ]]; then
  echo "ERROR: python3 not found. Install Python 3 first."
  exit 1
fi

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env — add FINNHUB_API_KEY before Refresh live data."
fi

if ! "$PYTHON" -c "import uvicorn" 2>/dev/null; then
  echo "Installing Python dependencies (one time)…"
  pip3 install -r "$ROOT/requirements.txt"
fi

mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

# Stop foreground/background process on 8080 if present
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
fi

# Unload old agent if reloading
launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${ROOT}/src</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${ROOT}/scripts/run_dashboard.py</string>
    <string>--port</string>
    <string>8080</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/dashboard.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/dashboard.err.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$PLIST_LABEL"
launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL"

sleep 2
if curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:8080/ | grep -q 200; then
  echo ""
  echo "Dashboard service installed and running."
  echo "  Open: http://127.0.0.1:8080"
  echo "  Logs: ${LOG_DIR}/dashboard.out.log"
  echo ""
  echo "No Terminal window needed. Starts automatically on login."
  echo "Stop:    ./scripts/uninstall_dashboard_service_mac.sh"
  echo "Restart: launchctl kickstart -k gui/$(id -u)/${PLIST_LABEL}"
else
  echo "Service installed but dashboard not responding yet."
  echo "Check logs: ${LOG_DIR}/dashboard.err.log"
  exit 1
fi
