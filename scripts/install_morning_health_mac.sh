#!/bin/bash
# Install LaunchAgents for morning health email/banner pings (Pacific wall clock).
#
# Default Pacific times (after morning_prep at 4:00 PT):
#   4:20  post-prep health
#   7:05  mid-morning health (optional; install both)
#
# Usage:
#   ./scripts/install_morning_health_mac.sh
#   ./scripts/install_morning_health_mac.sh --no-midmorning
#   ./scripts/install_morning_health_mac.sh --eastern   # 7:20 / 10:05 ET wall clock

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
RUNNER="$ROOT/scripts/run_morning_health_mac.sh"
LOG_DIR="$HOME/Library/Logs/investment-agent"

PACIFIC=1
MIDMORNING=1
for arg in "$@"; do
  case "$arg" in
    --pacific|--pt|--PST|--PDT) PACIFIC=1 ;;
    --eastern|--et|--EST|--EDT) PACIFIC=0 ;;
    --no-midmorning) MIDMORNING=0 ;;
    -h|--help)
      echo "Usage: $0 [--pacific|--eastern] [--no-midmorning]"
      exit 0
      ;;
  esac
done

if [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: .env missing — copy .env.example and add keys / SMTP_* for email."
  exit 1
fi

chmod +x "$RUNNER" "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

# hour minute label_suffix
if [[ "$PACIFIC" -eq 1 ]]; then
  schedule=(
    "4 20 morning"
  )
  if [[ "$MIDMORNING" -eq 1 ]]; then
    schedule+=("7 5 midmorning")
  fi
  clock_label="Pacific"
else
  schedule=(
    "7 20 morning"
  )
  if [[ "$MIDMORNING" -eq 1 ]]; then
    schedule+=("10 5 midmorning")
  fi
  clock_label="Eastern"
fi

install_job() {
  local hour="$1"
  local minute="$2"
  local suffix="$3"
  local label="com.investment-agent.health.${suffix}"
  local plist="$HOME/Library/LaunchAgents/${label}.plist"

  launchctl bootout "gui/$(id -u)/${label}" 2>/dev/null || true

  # Weekdays Mon–Fri via StartCalendarInterval array
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
    <key>PYTHONNOUSERSITE</key>
    <string>1</string>
    <key>NOTIFY_ON_SUCCESS</key>
    <string>1</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${RUNNER}</string>
    <string>--force-notify</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict>
      <key>Weekday</key><integer>1</integer>
      <key>Hour</key><integer>${hour}</integer>
      <key>Minute</key><integer>${minute}</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>2</integer>
      <key>Hour</key><integer>${hour}</integer>
      <key>Minute</key><integer>${minute}</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>3</integer>
      <key>Hour</key><integer>${hour}</integer>
      <key>Minute</key><integer>${minute}</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>4</integer>
      <key>Hour</key><integer>${hour}</integer>
      <key>Minute</key><integer>${minute}</integer>
    </dict>
    <dict>
      <key>Weekday</key><integer>5</integer>
      <key>Hour</key><integer>${hour}</integer>
      <key>Minute</key><integer>${minute}</integer>
    </dict>
  </array>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/health-${suffix}.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/health-${suffix}.err.log</string>
</dict>
</plist>
EOF

  launchctl bootstrap "gui/$(id -u)" "$plist"
  launchctl enable "gui/$(id -u)/${label}" 2>/dev/null || true
  echo "  $(printf '%02d:%02d' "$hour" "$minute")  health/${suffix}  ($label)"
}

for old in com.investment-agent.health.morning com.investment-agent.health.midmorning; do
  launchctl bootout "gui/$(id -u)/$old" 2>/dev/null || true
done

echo "Installing morning health LaunchAgents (${clock_label} wall clock)…"
for entry in "${schedule[@]}"; do
  read -r hour minute suffix <<<"$entry"
  install_job "$hour" "$minute" "$suffix"
done

echo ""
echo "Morning health installed."
echo "  Manual:  ./scripts/run_morning_health_mac.sh --force-notify"
echo "  Logs:    $LOG_DIR/health-*.log"
echo "  Email:   set SMTP_HOST / SMTP_USER / SMTP_PASSWORD in .env"
echo "           (without SMTP: still writes log + macOS banner)"
echo "  Unload:  launchctl bootout gui/\$(id -u)/com.investment-agent.health.morning"
echo ""
