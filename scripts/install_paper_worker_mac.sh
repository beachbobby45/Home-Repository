#!/bin/bash
# Install KeepAlive LaunchAgent for the INTERNAL paper ledger worker.
# No Robinhood. Dual arms: gate_approved + all_signals.
#
# Usage: ./scripts/install_paper_worker_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(cd "$PWD" && pwd)"
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/run_paper_worker.py" 2>/dev/null || true
PYTHON="$("$ROOT/scripts/resolve_python.sh")" || {
  echo "ERROR: No working Python (.venv). Run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
}
PLIST_LABEL="com.investment-agent.paper-worker"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/investment-agent"

echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"

# Do not install the dry-run RH execution worker for paper phase
if [[ -f "$HOME/Library/LaunchAgents/com.investment-agent.execution-worker.plist" ]]; then
  echo "Note: execution-worker plist exists — leaving it alone (paper-worker is separate)."
fi

launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true

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
    <key>PYTHONNOUSERSITE</key>
    <string>1</string>
    <key>EXECUTION_MODE</key>
    <string>paper</string>
  </dict>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${ROOT}/scripts/run_paper_worker.py</string>
    <string>--loop</string>
    <string>--interval</string>
    <string>60</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/paper-worker.out.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/paper-worker.err.log</string>
</dict>
</plist>
EOF

# Point Account / Capital Builder at the $5k paper book
PYTHONPATH="$ROOT/src" "$PYTHON" - <<'PY'
from investment_agent.db import connect, init_db
from investment_agent.execution.ops_audit import set_ledger_source
from investment_agent.execution.paper_ledger import PAPER_STARTING_CASH, ensure_paper_accounts
db = init_db()
conn = connect(db)
ensure_paper_accounts(conn, starting_cash=PAPER_STARTING_CASH)
set_ledger_source(conn, "paper")
conn.commit()
conn.close()
print("ledger_source=paper starting_cash=5000")
PY

launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true

echo ""
echo "Paper worker installed (INTERNAL ledger — no Robinhood)."
echo "  Logs:   $LOG_DIR/paper-worker.out.log"
echo "  Status: PYTHONPATH=src $PYTHON scripts/run_paper_worker.py --status-only"
echo "  Stop:   launchctl bootout gui/$(id -u)/$PLIST_LABEL"
echo ""
echo "Also reinstall intraday rhythm on Pacific wall clock:"
echo "  ./scripts/install_intraday_schedule_mac.sh --pacific"
