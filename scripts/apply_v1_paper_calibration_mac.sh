#!/bin/bash
# Apply v1 same-time paper calibration on Tony's Mac:
#   - Day gate PRODUCE (MA ≥50, bull gate soft)
#   - Special Watch (datacenter_us + extras) → active consideration pool
#   - Confirm constants: fill deadline 12:30 ET, RH $0 fees, STOP 0.75%
#
# Does NOT change stop %, lot targets ($75/$150), or add a strength arm.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/apply_v1_paper_calibration_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

echo "=== Apply v1 paper calibration (produce@50 + 12:30 + SW sync + RH fees) ==="
"$PY" - <<'PY'
import json
from investment_agent.account import get_day_gate_mode, set_day_gate_mode
from investment_agent.db import connect, init_db
from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE
from investment_agent.market_activity import FLIP_EXIT_MIN, PRODUCE_TRADE_MIN, TRADE_MIN
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE_LABEL
from investment_agent.strategy import STOP_PCT
from investment_agent.watchlist import sync_special_watch_into_consideration

conn = connect(init_db())
try:
    before = get_day_gate_mode(conn)
    mode = set_day_gate_mode(conn, "produce")
    sw = sync_special_watch_into_consideration(conn, "datacenter_us")
    conn.commit()
    out = {
        "ok": True,
        "day_gate_mode_before": before,
        "day_gate_mode": mode,
        "produce_trade_min": PRODUCE_TRADE_MIN,
        "preserve_trade_min": TRADE_MIN,
        "flip_exit_min": FLIP_EXIT_MIN,
        "limit_fill_deadline_et": LIMIT_FILL_DEADLINE_LABEL,
        "default_buy_fee": DEFAULT_BUY_FEE,
        "default_sell_fee": DEFAULT_SELL_FEE,
        "stop_pct": STOP_PCT,
        "special_watch_sync": sw,
    }
    print(json.dumps(out, indent=2))
    assert mode == "produce"
    assert PRODUCE_TRADE_MIN == 50
    assert LIMIT_FILL_DEADLINE_LABEL == "12:30 ET"
    assert DEFAULT_BUY_FEE == 0.0 and DEFAULT_SELL_FEE == 0.0
    assert abs(STOP_PCT - 0.75) < 1e-9
finally:
    conn.close()
PY

echo ""
echo "Done. Restart dashboard if it is already running so UI copy refreshes:"
echo "  ./scripts/restart_dashboard_mac.sh"
echo "Verify day gate:  curl -s http://127.0.0.1:8080/api/settings/day-gate-mode"
echo "Paper ≥2 weeks with fills before any mid-Nov live sketch."
