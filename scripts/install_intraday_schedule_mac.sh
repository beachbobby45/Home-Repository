#!/bin/bash
# Install LaunchAgents for intraday rhythm (Mac local wall clock).
#
# Default (ET wall clock — Mac timezone America/New_York):
#   7:00  morning_prep
#   9:31  at_open
#   …
#
# Pacific (--pacific) — Tony’s Mac on America/Los_Angeles (ET−3):
#   4:00  morning_prep
#   6:31  at_open
#   …
#
# Usage:
#   ./scripts/install_intraday_schedule_mac.sh
#   ./scripts/install_intraday_schedule_mac.sh --pacific

set -e
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
RHYTHM="$ROOT/scripts/run_intraday_rhythm_mac.sh"
LOG_DIR="$HOME/Library/Logs/investment-agent"

PACIFIC=0
for arg in "$@"; do
  case "$arg" in
    --pacific|--pt|--PST|--PDT) PACIFIC=1 ;;
    -h|--help)
      echo "Usage: $0 [--pacific]"
      exit 0
      ;;
  esac
done

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env missing — add FINNHUB_API_KEY first."
  exit 1
fi

chmod +x "$RHYTHM" "$ROOT/scripts/run_morning_prep_mac.sh" 2>/dev/null || true
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

# hour minute mode  — ET times; shifted −3h when PACIFIC=1
schedule_et=(
  "7 0 morning_prep"
  "9 31 at_open"
  "9 36 opening_drive"
  "9 41 opening_drive"
  "9 46 plus_15m"
  "10 0 trade_refresh"
  "11 0 trade_refresh"
  "12 0 trade_refresh"
  "13 0 trade_refresh"
  "14 0 trade_refresh"
)

labels=(
  com.investment-agent.intraday.morning
  com.investment-agent.intraday.atopen
  com.investment-agent.intraday.od936
  com.investment-agent.intraday.od941
  com.investment-agent.intraday.plus15
  com.investment-agent.intraday.t1000
  com.investment-agent.intraday.t1100
  com.investment-agent.intraday.t1200
  com.investment-agent.intraday.t1300
  com.investment-agent.intraday.t1400
)

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

for old in "${labels[@]}"; do
  launchctl bootout "gui/$(id -u)/$old" 2>/dev/null || true
done

i=0
for entry in "${schedule_et[@]}"; do
  read -r hour minute mode <<<"$entry"
  if [[ "$PACIFIC" -eq 1 ]]; then
    hour=$((10#$hour - 3))
    if [[ "$hour" -lt 0 ]]; then
      echo "ERROR: invalid Pacific hour for $mode"
      exit 1
    fi
  fi
  label="${labels[$i]}"
  install_job "$label" "$hour" "$minute" "$mode"
  echo "  $(printf '%02d:%02d' "$hour" "$minute")  $mode  ($label)"
  i=$((i + 1))
done

echo ""
if [[ "$PACIFIC" -eq 1 ]]; then
  echo "Intraday LaunchAgents installed for Pacific wall clock (ET−3)."
else
  echo "Intraday LaunchAgents installed for Eastern wall clock."
  echo "On a Pacific Mac, re-run: $0 --pacific"
fi
echo "Logs: $LOG_DIR/intraday-*.log"
echo "Uninstall: ./scripts/uninstall_intraday_schedule_mac.sh"
echo ""
