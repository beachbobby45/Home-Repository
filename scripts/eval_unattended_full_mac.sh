#!/bin/bash
# Full autonomous-path evaluation for tomorrow with NO operator input.
# Exits 0 only on AUTONOMOUS_READY.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/eval_unattended_full_mac.sh

set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
FAILS=0
FAIL_MSGS=()
ok() { echo "OK:   $*"; }
warn() { echo "WARN: $*"; }
bad() { echo "FAIL: $*"; FAILS=$((FAILS + 1)); FAIL_MSGS+=("$*"); }

echo "=== FULL UNATTENDED EVAL ($(date '+%Y-%m-%d %H:%M:%S %z')) ==="
echo "Repo: $ROOT"
echo ""

chmod +x \
  "$ROOT/scripts/doctor_paper_ready_mac.sh" \
  "$ROOT/scripts/arm_unattended_mac.sh" \
  "$ROOT/scripts/reopen_paper_waiting_mac.sh" \
  "$ROOT/scripts/run_paper_worker.py" \
  "$ROOT/scripts/run_morning_prep_mac.sh" \
  2>/dev/null || true

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"

echo "── 1) Code version (propose-race fix must be present) ──"
if grep -q "waiting_signal" "$ROOT/src/investment_agent/execution/paper_runner.py" 2>/dev/null; then
  ok "paper_runner has waiting_signal retry fix"
else
  bad "paper_runner missing waiting_signal fix — git pull cursor/post-pdt-strategy-refresh-cd1d"
fi
BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "?")
echo "Branch: $BRANCH @ $COMMIT"
echo ""

echo "── 2) Unit / process tests (paper path) ──"
TEST_MODS=(
  tests.test_paper_propose_race
  tests.test_unattended_paper_day
  tests.test_paper_ledger
  tests.test_paper_automation
)
# Include top-3 scorer tests when present on this checkout.
if [[ -f "$ROOT/tests/test_tradable_now.py" ]]; then
  TEST_MODS+=(tests.test_tradable_now)
fi
if [[ -f "$ROOT/tests/test_best_tradable_propose.py" ]]; then
  TEST_MODS+=(tests.test_best_tradable_propose)
fi
if ! "$PY" -m unittest "${TEST_MODS[@]}" -v; then
  bad "paper unit/process tests FAILED"
else
  ok "paper unit/process tests PASSED"
fi
echo ""

echo "── 3) LaunchAgents required for autonomy ──"
UID_N="$(id -u)"
need() {
  if launchctl print "gui/${UID_N}/$1" &>/dev/null; then
    ok "$1 loaded"
  else
    bad "$1 NOT loaded"
  fi
}
need "com.investment-agent.dashboard"
need "com.investment-agent.paper-worker"
need "com.investment-agent.intraday.morning"
need "com.investment-agent.health.morning"
# Verify paper worker is looping
if launchctl print "gui/${UID_N}/com.investment-agent.paper-worker" 2>/dev/null | grep -q "state = running"; then
  ok "paper-worker state=running"
else
  bad "paper-worker not running"
fi
echo ""

echo "── 4) Power (must not sleep overnight) ──"
if command -v pmset >/dev/null 2>&1; then
  SLEEP_VAL=$(pmset -g | awk '/^ sleep /{print $2; exit}')
  if [[ "${SLEEP_VAL:-}" == "0" ]]; then
    ok "system sleep=0"
  else
    bad "system sleep=${SLEEP_VAL:-?} — sudo pmset -c sleep 0 disksleep 0"
  fi
else
  bad "pmset missing"
fi
echo ""

echo "── 5) Dashboard + paper APIs ──"
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null || echo "000")
[[ "$HTTP" == "200" ]] && ok "dashboard HTTP 200" || bad "dashboard HTTP $HTTP"
for path in /api/paper/status /api/paper/sessions /api/daily-rhythm/candidates /api/ops/health /api/trading-day/status; do
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 "http://127.0.0.1:8080${path}" 2>/dev/null || echo "000")
  [[ "$CODE" == "200" ]] && ok "GET $path → 200" || bad "GET $path → $CODE"
done
echo ""

echo "── 6) Kill switch must be OFF ──"
KS=$("$PY" - <<'PY'
import json, urllib.request
try:
    with urllib.request.urlopen("http://127.0.0.1:8080/api/paper/status", timeout=10) as r:
        d = json.loads(r.read().decode())
    print("ON" if d.get("kill_switch_active") else "OFF")
except Exception as e:
    print(f"ERR:{e}")
PY
)
if [[ "$KS" == "OFF" ]]; then
  ok "STOP PROCESS / kill switch OFF"
elif [[ "$KS" == "ON" ]]; then
  bad "kill switch ON — automation blocked (turn STOP PROCESS off)"
else
  bad "kill switch check failed: $KS"
fi
echo ""

echo "── 7) Simulate overnight→prep race on a throwaway date ──"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1
SIM=$("$PY" - <<'PY'
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo
from investment_agent.db import connect, init_db
from investment_agent.execution import paper_runner
from investment_agent.execution.paper_ledger import ACCOUNT_GATE, ensure_paper_accounts, get_session_log
from investment_agent.execution.paper_runner import run_paper_tick

ET = ZoneInfo("America/New_York")
day = "2099-01-02"  # throwaway
conn = connect(init_db())
ensure_paper_accounts(conn, starting_cash=5000.0)
# wipe any prior throwaway rows
conn.execute("DELETE FROM paper_session_logs WHERE session_date_et = ?", (day,))
conn.commit()

def tick(when, signal=None, bars=None):
    no = {"ok": False, "error": "No top pick available to propose", "session_date_et": day}
    with patch.object(paper_runner, "is_kill_switch_active", return_value=False), \
         patch.object(paper_runner, "datetime") as dt, \
         patch.object(paper_runner, "_plan_signal", return_value=signal or no), \
         patch.object(paper_runner, "_fetch_day_bars", return_value=bars or []):
        dt.now.return_value = when
        return run_paper_tick(conn, session_date_et=day)

tick(datetime(2099, 1, 2, 0, 10, tzinfo=ET))
g1 = get_session_log(conn, day, ACCOUNT_GATE)
sig = {
    "ok": True, "session_date_et": day, "ticker": "SIM",
    "limit_buy": 99.5, "limit_sell": 101.0, "stop": 98.5,
    "shares": 50, "deploy": 5000.0, "allow_trade": True,
    "ma_score": 70, "day_gate_mode": "produce",
}
bars = [
    {"ts": "2099-01-02T09:35:00-04:00", "open": 100, "high": 100.5, "low": 99.0, "close": 99.8},
    {"ts": "2099-01-02T10:05:00-04:00", "open": 100, "high": 101.5, "low": 100, "close": 101.2},
]
tick(datetime(2099, 1, 2, 10, 30, tzinfo=ET), signal=sig, bars=bars)
g2 = get_session_log(conn, day, ACCOUNT_GATE)
conn.execute("DELETE FROM paper_session_logs WHERE session_date_et = ?", (day,))
conn.commit()
conn.close()
print(f"after_midnight={g1 and g1.get('status')}")
print(f"after_prep_fill={g2 and g2.get('status')}")
print(f"filled={g2 and g2.get('filled')}")
print("SIM_OK" if g1 and g1.get("status") == "waiting_signal" and g2 and g2.get("status") == "complete" and g2.get("filled") else "SIM_FAIL")
PY
)
echo "$SIM"
if echo "$SIM" | grep -q '^SIM_OK$'; then
  ok "overnight→prep→fill simulation PASSED"
else
  bad "overnight→prep→fill simulation FAILED"
fi
echo ""

echo "── 8) Doctor ──"
if "$ROOT/scripts/doctor_paper_ready_mac.sh"; then
  ok "doctor PAPER_STACK_OK"
else
  bad "doctor reported FAIL items"
fi
echo ""

echo "── 9) Clear stuck today rows so tomorrow starts clean ──"
"$ROOT/scripts/reopen_paper_waiting_mac.sh" || warn "reopen script exited non-zero"
echo ""

echo "=== FINAL VERDICT ==="
echo "Note: AUTONOMOUS_READY means process path is proven."
echo "It does NOT guarantee a fill tomorrow — that still needs a limit trade-through"
echo "on the selected name (best of top-3 on gate book) and Market Activity allow_trade=True."
if [[ "$FAILS" -eq 0 ]]; then
  echo "RESULT: AUTONOMOUS_READY"
  echo "Leave Mac on AC, sleep=0. No further input required for the process to run."
  exit 0
fi
echo "RESULT: NOT_READY ($FAILS issue(s))"
echo "Do not leave until this prints AUTONOMOUS_READY."
echo ""
echo "── Issues to fix ──"
for msg in "${FAIL_MSGS[@]:-}"; do
  echo "FAIL: $msg"
done
exit 1
