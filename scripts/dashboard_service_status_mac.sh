#!/bin/bash
# Check background dashboard service status (Mac).
# Usage: ./scripts/dashboard_service_status_mac.sh

PLIST_LABEL="com.investment-agent.dashboard"
LOG_DIR="$HOME/Library/Logs/investment-agent"

echo "=== Investment Agent Dashboard ==="
if launchctl print "gui/$(id -u)/$PLIST_LABEL" &>/dev/null; then
  echo "LaunchAgent: installed (running in background)"
else
  echo "LaunchAgent: not installed"
  echo "Install: ./scripts/install_dashboard_service_mac.sh"
fi

HTTP=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null || echo "000")
if [[ "$HTTP" == "200" ]]; then
  echo "Dashboard:   UP at http://127.0.0.1:8080"
else
  echo "Dashboard:   not responding on port 8080"
fi

if [[ -f "$LOG_DIR/dashboard.err.log" ]]; then
  echo ""
  echo "Recent errors (last 5 lines):"
  tail -5 "$LOG_DIR/dashboard.err.log"
fi
