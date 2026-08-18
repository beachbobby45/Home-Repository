#!/bin/bash
# Morning precheck — before you place limit orders (~6:30–9:30 AM local).
# 1) Optional incremental ingest (skip if after-close EOD ran last night)
# 2) Re-run screener + build Trade tab candidates
# Does NOT replace Step 3 — run ./scripts/run_refresh_live_mac.sh right before you buy.
#
# Usage:
#   ./scripts/run_morning_prep_mac.sh
#   ./scripts/run_morning_prep_mac.sh --with-ingest   # force incremental ingest first

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh"

WITH_INGEST=0
for arg in "$@"; do
  case "$arg" in
    --with-ingest) WITH_INGEST=1 ;;
  esac
done

echo ""
echo "  AI Investment Agent — morning prep"
echo "  Folder: $ROOT"
echo "  Python: $PY ($("$PY" --version 2>&1))"
echo ""

if [[ "$WITH_INGEST" -eq 1 ]]; then
  echo "── Incremental ingest ──"
  chmod +x "$ROOT/scripts/run_ingest_mac.sh" 2>/dev/null || true
  "$ROOT/scripts/run_ingest_mac.sh" --incremental
  echo ""
fi

echo "── Prepare today's trades (screener + candidates) ──"
"$PY" - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))
from investment_agent.db import connect, init_db
from investment_agent.daily_rhythm import build_trading_candidates
from investment_agent.period_screener import date_range_for_period, list_trading_dates, run_period_screener, save_screener_run
from investment_agent.screen_actions import ACTION_PERIOD_SCREENER, record_screen_action
from investment_agent.account import build_dashboard_summary
from investment_agent.trading_day import build_trading_day_status

conn = connect(init_db())
try:
    summary = build_dashboard_summary(conn)
    deploy = float(summary.tradable_cash or 10000)
    start, end = date_range_for_period(14, conn=conn)
    trading_dates = list_trading_dates(conn, count=14)
    result = run_period_screener(
        conn, start_date=start, end_date=end, tradable_cash=deploy,
        min_days_screened=1, trading_dates=trading_dates, requested_trading_days=14,
    )
    save_screener_run(conn, result)
    record_screen_action(conn, ACTION_PERIOD_SCREENER, detail=f"Morning prep · {len(result.get('candidates', []))} candidates")
    candidates = build_trading_candidates(conn, limit=15, period_days=14)
    status = build_trading_day_status(conn)
    conn.commit()
    print(json.dumps({
        "candidate_count": len(candidates),
        "top_pick": (status.get("top_pick") or {}).get("ticker"),
        "verdict": status.get("verdict"),
        "headline": status.get("headline"),
    }, indent=2))
finally:
    conn.close()
PY

echo ""
echo "Next: open dashboard → Trade tab → Refresh live before buy"
echo "Or:  ./scripts/run_refresh_live_mac.sh"
echo ""
