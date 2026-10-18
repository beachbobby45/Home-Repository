#!/bin/bash
# Install macOS LaunchAgent for the execution worker (dry-run sync/status).
# Does NOT place live orders until Robinhood client + EXECUTION_LIVE are configured.
# Usage: ./scripts/install_execution_worker_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/run_execution_worker.py" 2>/dev/null || true
PYTHON="$("$ROOT/scripts/resolve_python.sh")" || {
  echo "ERROR: No working Python (.venv). Run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
}
PLIST_LABEL="com.investment-agent.execution-worker"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"

echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

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
    <string>${ROOT}/scripts/run_execution_worker.py</string>
    <string>--loop</string>
    <string>--interval</string>
    <string>60</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/execution-worker.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/execution-worker.err.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true

echo ""
echo "Execution worker installed (dry-run sync loop)."
echo "  Logs: $LOG_DIR/execution-worker.out.log"
echo "  Stop: launchctl bootout gui/$(id -u)/$PLIST_LABEL"
echo "  Live orders: NOT enabled (needs Robinhood client + EXECUTION_LIVE=1)"
