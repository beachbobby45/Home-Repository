#!/bin/bash
# Install LaunchAgents for intraday rhythm (Mac local time ≈ ET when Mac is on ET).
#
# Schedule (ET-oriented — set Mac clock/timezone to America/New_York):
#   7:00  morning_prep  — ingest + screener + pre_market snapshot
#   9:31  at_open       — live refresh + at_open snapshot
#   9:36  opening_drive — Opening Drive refresh #1
#   9:41  opening_drive — Opening Drive refresh #2
#   9:46  plus_15m      — live refresh + plus_15m snapshot
#   10:00 trade_refresh — first post-gate refresh
#   11:00, 12:00, 13:00, 14:00 — periodic refresh until cutoff
#
# Usage: ./scripts/install_intraday_schedule_mac.sh

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
RHYTHM="$ROOT/scripts/run_intraday_rhythm_mac.sh"
LOG_DIR="$HOME/Library/Logs/investment-agent"

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env missing — add FINNHUB_API_KEY first."
  exit 1
fi

chmod +x "$RHYTHM" "$ROOT/scripts/run_morning_prep_mac.sh" 2>/dev/null || true
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

install_job() {
  local label="$1"
  local hour="$2"
  local minute="$3"
  local mode="$4"
  local plist="$HOME/Library/LaunchAgents/${label}.plist"

  launchctl bootout "gui/$(id -u)/${label}" 2>/dev/null || true

  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label}</string>
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
    <string>${RHYTHM}</string>
    <string>${mode}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${hour}</integer>
    <key>Minute</key>
    <integer>${minute}</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/intraday-${mode}-${hour}${minute}.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/intraday-${mode}-${hour}${minute}.err.log</string>
</dict>
</plist>
EOF

  launchctl bootstrap "gui/$(id -u)" "$plist"
  launchctl enable "gui/$(id -u)/${label}"
}

# Uninstall previous intraday labels if re-running
for old in com.investment-agent.intraday.morning \
           com.investment-agent.intraday.atopen \
           com.investment-agent.intraday.od936 \
           com.investment-agent.intraday.od941 \
           com.investment-agent.intraday.plus15 \
           com.investment-agent.intraday.t1000 \
           com.investment-agent.intraday.t1100 \
           com.investment-agent.intraday.t1200 \
           com.investment-agent.intraday.t1300 \
           com.investment-agent.intraday.t1400; do
  launchctl bootout "gui/$(id -u)/$old" 2>/dev/null || true
done

install_job com.investment-agent.intraday.morning 7 0 morning_prep
install_job com.investment-agent.intraday.atopen 9 31 at_open
install_job com.investment-agent.intraday.od936 9 36 opening_drive
install_job com.investment-agent.intraday.od941 9 41 opening_drive
install_job com.investment-agent.intraday.plus15 9 46 plus_15m
install_job com.investment-agent.intraday.t1000 10 0 trade_refresh
install_job com.investment-agent.intraday.t1100 11 0 trade_refresh
install_job com.investment-agent.intraday.t1200 12 0 trade_refresh
install_job com.investment-agent.intraday.t1300 13 0 trade_refresh
install_job com.investment-agent.intraday.t1400 14 0 trade_refresh

echo ""
echo "Intraday LaunchAgents installed (Mac local time — use ET timezone):"
echo "  7:00   morning_prep"
echo "  9:31   at_open"
echo "  9:36   opening_drive"
echo "  9:41   opening_drive"
echo "  9:46   plus_15m"
echo "  10:00–14:00 hourly trade_refresh"
echo ""
echo "Logs: $LOG_DIR/intraday-*.log"
echo "Uninstall: ./scripts/uninstall_intraday_schedule_mac.sh"
echo "Manual:    ./scripts/run_intraday_rhythm_mac.sh opening_drive"
echo ""
