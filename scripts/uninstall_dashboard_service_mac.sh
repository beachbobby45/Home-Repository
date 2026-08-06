#!/bin/bash
# Remove background dashboard LaunchAgent.
# Usage: ./scripts/uninstall_dashboard_service_mac.sh

set -e
PLIST_LABEL="com.investment-agent.dashboard"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
rm -f "$PLIST_PATH"

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  [[ -n "$PIDS" ]] && kill $PIDS 2>/dev/null || true
fi

echo "Dashboard background service stopped and removed."
