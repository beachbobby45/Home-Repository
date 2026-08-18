#!/bin/bash
# End-of-day pipeline — run after market close (~4:30 PM local or later).
# 1) Refresh quotes + daily bars for full watchlist
# 2) Rebuild 14-day ranked screener (pullback $ metrics)
# 3) Save daily close report for Review tab
#
# Usage:
#   ./scripts/run_end_of_day_mac.sh
#   ./scripts/run_end_of_day_mac.sh --skip-report   # ingest + screener only

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"
SKIP_REPORT=0
for arg in "$@"; do
  case "$arg" in
    --skip-report) SKIP_REPORT=1 ;;
  esac
done

echo ""
echo "  AI Investment Agent — end of day"
echo "  Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo "  Steps: after-close ingest → screener → daily close report"
echo ""

chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true

echo "── Step 1/3: After-close ingest (~15–25 min for S&P 500) ──"
"$ROOT/scripts/run_ingest_mac.sh" --after-close

echo ""
echo "── Step 2/3: Ranked screener (14 trading days) ──"
"$PY" "$ROOT/scripts/run_period_screener.py" --days 14 --save >/dev/null
"$PY" - <<'PY'
import json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from investment_agent.db import connect, init_db
from investment_agent.screen_actions import ACTION_PERIOD_SCREENER, record_screen_action

conn = connect(init_db())
try:
    n = conn.execute("SELECT COUNT(*) AS c FROM screener_runs").fetchone()["c"]
    record_screen_action(conn, ACTION_PERIOD_SCREENER, detail=f"EOD pipeline · run #{n}")
    conn.commit()
finally:
    conn.close()
print("Screener saved.")
PY

if [[ "$SKIP_REPORT" -eq 0 ]]; then
  echo ""
  echo "── Step 3/3: Daily close report ──"
  "$PY" "$ROOT/scripts/run_daily_close.py" --daily
fi

echo ""
echo "── Freshness check ──"
"$PY" "$ROOT/scripts/manage_watchlist.py" stats | "$PY" -c "
import json, sys
s = json.load(sys.stdin)
f = s.get('freshness', {})
print('Newest quote:', f.get('quotes_newest_at', '—'))
print('Newest metrics:', f.get('metrics_newest_at', '—'))
print('Step 3 pass:', s.get('pass_both_step3'), 'of', s.get('tradeable_universe'))
"

echo ""
echo "Done. Tomorrow: Trade tab → Prepare today's trades, then Refresh live before buy."
echo "Or run: ./scripts/run_morning_prep_mac.sh"
echo ""
