#!/bin/bash
# Remove intraday LaunchAgents installed by install_intraday_schedule_mac.sh

set -e
for label in com.investment-agent.intraday.morning \
             com.investment-agent.intraday.atopen \
             com.investment-agent.intraday.od936 \
             com.investment-agent.intraday.od941 \
             com.investment-agent.intraday.plus15 \
             com.investment-agent.intraday.t1000 \
             com.investment-agent.intraday.t1100 \
             com.investment-agent.intraday.t1200 \
             com.investment-agent.intraday.t1300 \
             com.investment-agent.intraday.t1400; do
  launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
  rm -f "$HOME/Library/LaunchAgents/${label}.plist"
done
echo "Intraday schedule uninstalled."
