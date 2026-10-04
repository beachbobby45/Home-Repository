#!/bin/bash
# Install macOS LaunchAgent — dashboard runs in background (no Terminal window).
# Usage: ./scripts/install_dashboard_service_mac.sh
# Open: http://127.0.0.1:8080

set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/run_dashboard.py" 2>/dev/null || true
PYTHON="$("$ROOT/scripts/resolve_python.sh")" || {
  echo "ERROR: No working Python (.venv). Run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
}
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"
URL="http://127.0.0.1:8080"

echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"
echo ""

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env — add FINNHUB_API_KEY before Refresh live data."
fi

if ! PYTHONNOUSERSITE=1 "$PYTHON" -c "import uvicorn, fastapi, jinja2" 2>/dev/null; then
  echo "Installing Python dependencies into .venv…"
  PYTHONNOUSERSITE=1 "$PYTHON" -m pip install -r "$ROOT/requirements.txt"
fi

if ! PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$PYTHON" -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
  echo "ERROR: Dashboard app cannot import — fix Python before starting service."
  PYTHONNOUSERSITE=1 PYTHONPATH="$ROOT/src" "$PYTHON" -c "from investment_agent.dashboard.app import app" 2>&1 | tail -10
  echo ""
  echo "Run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
fi

mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
  sleep 1
fi

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
    <key>PYTHONNOUSERSITE</key>
    <string>1</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${ROOT}/scripts/run_dashboard.py</string>
    <string>--host</string>
    <string>127.0.0.1</string>
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

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || {
  echo "LaunchAgent already loaded — reloading plist…"
  launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
}
launchctl enable "gui/$(id -u)/$PLIST_LABEL"
# Fresh stderr for this start — avoids stale NumPy arch lines from prior crashes.
: > "${LOG_DIR}/dashboard.err.log" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL"

HEALTH_WAIT_SEC="${DASHBOARD_HEALTH_WAIT_SEC:-60}"
echo "Waiting for dashboard service (up to ${HEALTH_WAIT_SEC}s)…"
CODE="000"
for _ in $(seq 1 "$HEALTH_WAIT_SEC"); do
  sleep 1
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/version" 2>/dev/null || echo "000")
  if [[ "$CODE" == "200" ]]; then
    echo ""
    echo "Dashboard service installed and running."
    echo "  Open: $URL"
    echo "  Logs: ${LOG_DIR}/dashboard.out.log"
    echo ""
    echo "No Terminal window needed. Starts automatically on login."
    echo "Stop:    ./scripts/uninstall_dashboard_service_mac.sh"
    echo "Restart: launchctl kickstart -k gui/$(id -u)/${PLIST_LABEL}"
    exit 0
  fi
done

echo ""
echo "ERROR: Dashboard service installed but not responding (last HTTP ${CODE})."
RECENT_ERR="$(tail -20 "${LOG_DIR}/dashboard.err.log" 2>/dev/null || true)"
if echo "$RECENT_ERR" | grep -qi "incompatible architecture\|mach-o.*wrong"; then
  echo ""
  echo "NumPy/Python architecture mismatch detected in service log."
  echo "Fix: ./scripts/fix_ingest_python_mac.sh"
  echo "Or:  Finder → Repair Dashboard.command"
fi
echo "--- ${LOG_DIR}/dashboard.err.log (last 25 lines) ---"
tail -25 "${LOG_DIR}/dashboard.err.log" 2>/dev/null || echo "(no stderr log yet)"
echo "--- ${LOG_DIR}/dashboard.out.log (last 10 lines) ---"
tail -10 "${LOG_DIR}/dashboard.out.log" 2>/dev/null || echo "(no stdout log yet)"
echo ""
echo "Fix: ./scripts/fix_ingest_python_mac.sh && ./scripts/install_dashboard_service_mac.sh"
echo "Or:  ./scripts/doctor_dashboard_mac.sh"
exit 1
