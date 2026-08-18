#!/bin/bash
# Open the Desktop app's last script output in TextEdit (full log — easy to copy).
set -u
LOG="$HOME/.investment_agent/last-run.log"
mkdir -p "$(dirname "$LOG")"
if [[ ! -f "$LOG" ]]; then
  echo "No last run log yet." > "$LOG"
  echo "Run Morning Prep, Refresh Live, or End of Day in the Desktop app first." >> "$LOG"
fi
open -a TextEdit "$LOG"
