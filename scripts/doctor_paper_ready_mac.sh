#!/bin/bash
# Readiness check for Oct–Nov paper ledger (no Robinhood required).
# Paste the full output back to Cursor for confirmation.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/doctor_paper_ready_mac.sh

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"

ok() { echo "OK:   $*"; }
warn() { echo "WARN: $*"; }
bad() { echo "FAIL: $*"; FAILS=$((FAILS + 1)); }
FAILS=0

echo "=== Paper-ready doctor ($(date '+%Y-%m-%d %H:%M:%S %z')) ==="
echo "Repo: $ROOT"
echo "Host: $(scutil --get ComputerName 2>/dev/null || hostname)"
echo "User: $(whoami)"
echo ""

echo "── Git ──"
BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "?")
echo "Branch: $BRANCH @ $COMMIT"
if git -C "$ROOT" status -sb 2>/dev/null; then :; fi
echo ""

echo "── Timezone (PST OK; schedules must use PT wall clock) ──"
TZ_NAME=$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||' || true)
if [[ -z "${TZ_NAME:-}" ]]; then
  TZ_NAME=$(systemsetup -gettimezone 2>/dev/null | awk -F': ' '{print $2}' || true)
fi
echo "Timezone: ${TZ_NAME:-unknown}"
echo "Local now: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "ET now:    $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"
case "${TZ_NAME:-}" in
  America/Los_Angeles|US/Pacific|PST|PDT)
    ok "Mac on Pacific — paper LaunchAgents will use PT offsets (not ET clock)"
    ;;
  America/New_York|US/Eastern|EST|EDT)
    ok "Mac on Eastern — stock ET LaunchAgent hours match"
    ;;
  *)
    warn "Timezone is '${TZ_NAME:-unknown}' — tell Cursor so schedules can be offset"
    ;;
esac
echo ""

echo "── Power (need AC sleep=0; no caffeinate required) ──"
if command -v pmset >/dev/null 2>&1; then
  pmset -g | egrep 'sleep|disksleep|displaysleep|lowpowermode|powernap|hibernatemode|womp' || true
  SLEEP_VAL=$(pmset -g | awk '/^ sleep /{print $2; exit}')
  DISK_VAL=$(pmset -g | awk '/^ disksleep /{print $2; exit}')
  if [[ "${SLEEP_VAL:-}" == "0" ]]; then
    ok "system sleep=0 (always-on policy)"
  else
    bad "system sleep=${SLEEP_VAL:-?} — run: sudo pmset -c sleep 0"
  fi
  if [[ "${DISK_VAL:-}" == "0" ]]; then
    ok "disksleep=0"
  else
    warn "disksleep=${DISK_VAL:-?} — preferred 0: sudo pmset -c disksleep 0"
  fi
else
  bad "pmset not available"
fi

if pgrep -x caffeinate >/dev/null 2>&1; then
  warn "caffeinate still running (pids: $(pgrep -x caffeinate | tr '\n' ' ')) — optional; killall caffeinate if you want it gone"
else
  ok "caffeinate not running"
fi
echo ""

echo "── Python / env ──"
chmod +x "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true
if PY=$("$ROOT/scripts/resolve_python.sh" 2>/dev/null); then
  ok "Python: $PY ($("$PY" --version 2>&1))"
else
  bad "no working .venv — run: ./scripts/fix_ingest_python_mac.sh"
  PY=""
fi
if [[ -f "$ROOT/.env" ]]; then
  ok ".env present"
  if grep -qE '^FINNHUB_API_KEY=.+' "$ROOT/.env" 2>/dev/null; then
    ok "FINNHUB_API_KEY set (value not printed)"
  else
    warn "FINNHUB_API_KEY missing/empty — market data / rhythm may fail"
  fi
else
  bad ".env missing — needed for market data (not Robinhood)"
fi
# Paper must NOT require RH secrets
if grep -qiE '^(ROBINHOOD_|RH_|EXECUTION_LIVE=1)' "$ROOT/.env" 2>/dev/null; then
  warn "Robinhood / live execution vars present in .env — paper phase should not submit live orders"
else
  ok "no obvious Robinhood/live submit vars in .env"
fi
echo ""

echo "── Dashboard LaunchAgent ──"
DASH_LABEL="com.investment-agent.dashboard"
if launchctl print "gui/$(id -u)/$DASH_LABEL" &>/dev/null; then
  ok "dashboard LaunchAgent loaded"
else
  bad "dashboard LaunchAgent not loaded — run: ./scripts/install_dashboard_service_mac.sh"
fi
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null || echo "000")
if [[ "$HTTP" == "200" ]]; then
  ok "dashboard HTTP 200 at http://127.0.0.1:8080"
else
  bad "dashboard not responding (HTTP $HTTP) — run: ./scripts/hard_restart_dashboard_mac.sh"
fi
echo ""

echo "── Intraday / related LaunchAgents ──"
AGENTS=$(launchctl list 2>/dev/null | grep investment-agent || true)
if [[ -n "$AGENTS" ]]; then
  echo "$AGENTS"
  if echo "$AGENTS" | grep -q 'intraday'; then
    ok "intraday schedule agents present"
  else
    warn "no intraday.* agents — paper needs ranks/gate; install: ./scripts/install_intraday_schedule_mac.sh"
    warn "NOTE: stock installer uses ET wall clock; on Pacific we must reinstall with PT offsets when building paper"
  fi
  if echo "$AGENTS" | grep -q 'paper-worker'; then
    ok "paper-worker LaunchAgent loaded"
  else
    warn "paper-worker not loaded — install: ./scripts/install_paper_worker_mac.sh"
  fi
  if echo "$AGENTS" | grep -q 'execution-worker'; then
    warn "execution-worker loaded — paper phase should use paper-worker only (no RH submit)"
  fi
else
  warn "no investment-agent jobs in launchctl list"
fi
echo ""

echo "── Paper artifacts ──"
for f in \
  scripts/install_paper_worker_mac.sh \
  scripts/run_paper_worker.py \
  src/investment_agent/execution/paper_ledger.py \
  src/investment_agent/execution/paper_runner.py
do
  if [[ -e "$ROOT/$f" ]]; then
    ok "found $f"
  else
    bad "missing $f — git pull paper branch"
  fi
done
echo ""

echo "── Paper API (if dashboard up) ──"
PCODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/api/paper/status 2>/dev/null || echo "000")
if [[ "$PCODE" == "200" ]]; then
  ok "GET /api/paper/status → 200"
else
  warn "GET /api/paper/status → HTTP $PCODE (restart dashboard after pull if missing)"
fi
echo ""

echo "── Disk / path ──"
ok "HOME=$HOME"
if [[ -d "$ROOT/data" ]]; then
  ok "data/ directory exists"
else
  warn "data/ missing — will be created for paper ledger"
fi
df -h "$ROOT" 2>/dev/null | tail -1 || true
echo ""

echo "=== Summary ==="
if [[ "$FAILS" -eq 0 ]]; then
  echo "RESULT: PAPER_STACK_OK (no FAIL items)"
  echo "If paper-worker WARN above: ./scripts/install_paper_worker_mac.sh"
  echo "Pacific intraday: ./scripts/install_intraday_schedule_mac.sh --pacific"
else
  echo "RESULT: NOT_READY ($FAILS FAIL item(s) — fix those first)"
fi
echo "Paste everything above back to Cursor."
exit "$FAILS"
