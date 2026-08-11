#!/bin/bash
# Remove scheduled ingest LaunchAgents.
# Usage: ./scripts/uninstall_ingest_schedule_mac.sh

set -e
PLIST_LABEL="com.investment-agent.ingest"
PLIST_AFTER="${PLIST_LABEL}.afterclose"

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$PLIST_AFTER" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
rm -f "$HOME/Library/LaunchAgents/${PLIST_AFTER}.plist"

echo "Scheduled ingest removed."
