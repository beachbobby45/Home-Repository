#!/bin/bash
# Install automatic daily ingest (no Terminal typing).
# Runs: 6:30 AM incremental + 4:30 PM after-close refresh (Mac local time).
# Mac must be awake at those times (or ingest runs at next wake).
# Usage: ./scripts/install_ingest_schedule_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
PLIST_LABEL="com.investment-agent.ingest"
PLIST_AFTER="${PLIST_LABEL}.afterclose"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PLIST_AFTER_PATH="$HOME/Library/LaunchAgents/${PLIST_AFTER}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"
SCHEDULE_SCRIPT="$ROOT/scripts/run_ingest_scheduled_mac.sh"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env missing — add FINNHUB_API_KEY and FRED_API_KEY first."
  exit 1
fi

chmod +x "$SCHEDULE_SCRIPT" "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$PLIST_AFTER" 2>/dev/null || true

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
    <string>/bin/bash</string>
    <string>${SCHEDULE_SCRIPT}</string>
    <string>morning</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>6</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/ingest-morning.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/ingest-morning.err.log</string>
</dict>
</plist>
EOF

cat > "$PLIST_AFTER_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_AFTER}</string>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>${ROOT}/src</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCHEDULE_SCRIPT}</string>
    <string>afterclose</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>16</integer>
    <key>Minute</key>
    <integer>30</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/ingest-afterclose.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/ingest-afterclose.err.log</string>
</dict>
</plist>
EOF

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$PLIST_LABEL"
launchctl bootstrap "gui/$(id -u)" "$PLIST_AFTER_PATH"
launchctl enable "gui/$(id -u)/$PLIST_AFTER"

echo ""
echo "Automatic ingest installed (Mac local time):"
echo "  6:30 AM  — morning incremental ingest"
echo "  4:30 PM  — after-close ingest + screener + daily close report"
echo ""
echo "Logs: $LOG_DIR/ingest.log"
echo "Manual EOD:  double-click scripts/Run End of Day.command"
echo "Manual AM:   double-click scripts/Run Morning Prep.command"
echo "Before buy:  double-click scripts/Run Refresh Live.command"
echo "Uninstall:   ./scripts/uninstall_ingest_schedule_mac.sh"
echo ""
echo "Note: Mac must be on (or awake) at scheduled times."
