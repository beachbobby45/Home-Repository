#!/bin/bash
# Start or restart the dashboard on 127.0.0.1:8080 (KeepAlive LaunchAgent preferred).
# Usage: ./scripts/ensure_dashboard_mac.sh
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
URL="http://127.0.0.1:8080"
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"

_dashboard_up() {
  curl -sf --connect-timeout 2 "$URL/api/version" >/dev/null 2>&1
}

if _dashboard_up; then
  echo "Dashboard already running at $URL"
  exit 0
fi

echo "Dashboard not responding — installing / restarting KeepAlive service…"
if ! "$ROOT/scripts/install_dashboard_service_mac.sh"; then
  echo "ERROR: Could not start dashboard service." >&2
  echo "Run: ./scripts/doctor_dashboard_mac.sh" >&2
  exit 1
fi

for _ in $(seq 1 25); do
  if _dashboard_up; then
    echo "Dashboard ready at $URL"
    if command -v open >/dev/null 2>&1; then
      open "$URL"
    fi
    exit 0
  fi
  sleep 1
done

echo "ERROR: Dashboard did not respond at $URL" >&2
echo "Logs: ${LOG_DIR}/dashboard.err.log" >&2
tail -20 "${LOG_DIR}/dashboard.err.log" 2>/dev/null || true
exit 1
