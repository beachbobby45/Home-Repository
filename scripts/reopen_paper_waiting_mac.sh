#!/bin/bash
# Clear premature no_signal / waiting_signal rows for today so the paper worker
# can propose again after morning prep. Safe: does not touch filled/complete days.
#
# Usage:
#   ./scripts/reopen_paper_waiting_mac.sh
#   ./scripts/reopen_paper_waiting_mac.sh 2026-10-22

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"
DAY="${1:-}"

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

"$PY" - <<PY
from investment_agent.db import connect, init_db
from investment_agent.trading_day import today_et_str

day = "${DAY}" or today_et_str()
conn = connect(init_db())
try:
    cur = conn.execute(
        """
        DELETE FROM paper_session_logs
        WHERE session_date_et = ?
          AND status IN ('no_signal', 'waiting_signal')
          AND IFNULL(filled, 0) = 0
          AND (
            scenario IN ('propose_failed', 'no_top_pick')
            OR lower(IFNULL(detail, '')) LIKE '%no top pick%'
            OR status = 'waiting_signal'
          )
        """,
        (day,),
    )
    conn.commit()
    print(f"Reopened waiting/propose-failed rows for {day}: deleted={cur.rowcount}")
finally:
    conn.close()
PY

echo "Kicking paper worker…"
launchctl kickstart -k "gui/$(id -u)/com.investment-agent.paper-worker" 2>/dev/null || true
sleep 2
echo "Done. Check Auto → Paper transactions, or:"
echo "  curl -s http://127.0.0.1:8080/api/paper/status | python3 -m json.tool | head -80"
