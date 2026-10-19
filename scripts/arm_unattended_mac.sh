#!/bin/bash
# Arm the Mac for unattended paper days. Installs schedules and proves the
# operator bar (no SMTP required):
#   1) macOS banner notifications work
#   2) dashboard up with ranked list / #1 pick / paper trade log APIs
#   3) paper-worker + morning_prep LaunchAgents loaded, sleep=0
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/arm_unattended_mac.sh
#   ./scripts/arm_unattended_mac.sh --no-pull

set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
FAILS=0
PULL=1
for arg in "$@"; do
  case "$arg" in
    --no-pull) PULL=0 ;;
    -h|--help)
      echo "Usage: $0 [--no-pull]"
      exit 0
      ;;
  esac
done

ok() { echo "OK:   $*"; }
warn() { echo "WARN: $*"; }
bad() { echo "FAIL: $*"; FAILS=$((FAILS + 1)); }

echo "=== Arm unattended Mac ($(date '+%Y-%m-%d %H:%M:%S %z')) ==="
echo "Repo: $ROOT"
echo "Bar:  banners + dashboard ranks/#1/paper log (SMTP optional)"
echo ""

if [[ "$PULL" -eq 1 ]]; then
  echo "── Git pull ──"
  git fetch origin cursor/post-pdt-strategy-refresh-cd1d 2>&1 || warn "fetch failed (continuing with local tree)"
  git checkout cursor/post-pdt-strategy-refresh-cd1d 2>&1 || warn "checkout failed — staying on $(git rev-parse --abbrev-ref HEAD)"
  git pull origin cursor/post-pdt-strategy-refresh-cd1d 2>&1 || warn "pull failed — using current commit"
  echo "Branch: $(git rev-parse --abbrev-ref HEAD) @ $(git rev-parse --short HEAD)"
  echo ""
fi

chmod +x \
  "$ROOT/scripts/doctor_paper_ready_mac.sh" \
  "$ROOT/scripts/install_paper_worker_mac.sh" \
  "$ROOT/scripts/install_intraday_schedule_mac.sh" \
  "$ROOT/scripts/install_morning_health_mac.sh" \
  "$ROOT/scripts/hard_restart_dashboard_mac.sh" \
  "$ROOT/scripts/run_morning_health_mac.sh" \
  "$ROOT/scripts/run_morning_prep_mac.sh" \
  "$ROOT/scripts/install_dashboard_service_mac.sh" \
  2>/dev/null || true

if [[ ! -f "$ROOT/.env" ]]; then
  bad ".env missing — copy .env.example and set FINNHUB_API_KEY before arming"
  echo "RESULT: NOT_READY"
  exit 1
fi

# shellcheck disable=SC1091
set -a
# shellcheck disable=SC1090
source "$ROOT/.env" 2>/dev/null || true
set +a
if [[ -z "${FINNHUB_API_KEY:-}" ]]; then
  bad "FINNHUB_API_KEY not set — morning prep / ranked list will be empty"
else
  ok "FINNHUB_API_KEY set"
fi
if [[ "${NOTIFY_ENABLED:-1}" == "0" ]]; then
  warn "NOTIFY_ENABLED=0 — macOS banners for health/paper may be off"
else
  ok "NOTIFY_ENABLED on (banners; SMTP optional)"
fi
if [[ -z "${SMTP_HOST:-}" || -z "${SMTP_USER:-}" || -z "${SMTP_PASSWORD:-}" ]]; then
  ok "SMTP not configured — email skipped (OK per operator); banners + dashboard are the notify path"
else
  ok "SMTP_* present (optional email also available)"
fi

# Timezone → schedule flavor
TZ_NAME=$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||' || true)
PACIFIC_FLAG=""
HEALTH_FLAG=""
case "${TZ_NAME:-}" in
  America/Los_Angeles|US/Pacific|PST|PDT)
    PACIFIC_FLAG="--pacific"
    HEALTH_FLAG=""
    ok "Timezone Pacific — installing PT wall-clock schedules"
    ;;
  America/New_York|US/Eastern|EST|EDT)
    PACIFIC_FLAG=""
    HEALTH_FLAG="--eastern"
    ok "Timezone Eastern — installing ET wall-clock schedules"
    ;;
  *)
    warn "Timezone '${TZ_NAME:-unknown}' — defaulting to Pacific schedule offsets"
    PACIFIC_FLAG="--pacific"
    HEALTH_FLAG=""
    ;;
esac
echo ""

echo "── Install dashboard / paper / intraday / morning health ──"
# launchctl bootstrap can return I/O error 5 when already loaded; hard restart is the real proof.
if [[ -x "$ROOT/scripts/install_dashboard_service_mac.sh" ]]; then
  if ! "$ROOT/scripts/install_dashboard_service_mac.sh"; then
    warn "dashboard install reported an error — will rely on hard_restart next"
  fi
else
  warn "install_dashboard_service_mac.sh missing — trying hard restart only"
fi
"$ROOT/scripts/install_paper_worker_mac.sh" || bad "paper-worker install failed"
"$ROOT/scripts/install_intraday_schedule_mac.sh" $PACIFIC_FLAG || bad "intraday schedule install failed"
"$ROOT/scripts/install_morning_health_mac.sh" $HEALTH_FLAG || bad "morning health install failed"
"$ROOT/scripts/hard_restart_dashboard_mac.sh" || bad "dashboard restart failed"
echo ""

echo "── Verify LaunchAgents loaded ──"
UID_N="$(id -u)"
need_loaded() {
  local label="$1"
  if launchctl print "gui/${UID_N}/${label}" &>/dev/null; then
    ok "$label loaded"
  else
    bad "$label NOT loaded"
  fi
}
need_loaded "com.investment-agent.dashboard"
need_loaded "com.investment-agent.paper-worker"
need_loaded "com.investment-agent.intraday.morning"
need_loaded "com.investment-agent.health.morning"
if launchctl print "gui/${UID_N}/com.investment-agent.health.midmorning" &>/dev/null; then
  ok "com.investment-agent.health.midmorning loaded"
else
  warn "midmorning health agent not loaded (morning-only is OK)"
fi
echo ""

echo "── Power (unattended needs sleep=0 on AC) ──"
if command -v pmset >/dev/null 2>&1; then
  SLEEP_VAL=$(pmset -g | awk '/^ sleep /{print $2; exit}')
  if [[ "${SLEEP_VAL:-}" == "0" ]]; then
    ok "system sleep=0"
  else
    bad "system sleep=${SLEEP_VAL:-?} — while on AC run: sudo pmset -c sleep 0 disksleep 0"
    echo "      Without this, morning prep / ranks often miss while you are away."
  fi
else
  bad "pmset unavailable"
fi
echo ""

echo "── Morning prep (ranked list + #1 pick for dashboard) ──"
if ! "$ROOT/scripts/run_morning_prep_mac.sh" --with-ingest; then
  bad "morning prep failed — dashboard will not have today's ranked list / #1"
else
  ok "morning prep finished"
fi
echo ""

echo "── Dashboard proof: ranks / #1 / paper status ──"
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:8080/ 2>/dev/null || echo "000")
if [[ "$HTTP" == "200" ]]; then
  ok "dashboard HTTP 200"
else
  bad "dashboard not responding (HTTP $HTTP)"
fi

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
PROOF=$("$PY" - <<'PY' 2>&1) || true
import json
import os
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:8080{path}", timeout=20) as r:
        return json.loads(r.read().decode())

day = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
ok_all = True
notes = []
pick = None
ranked_n = 0

try:
    paper = get("/api/paper/status")
    eq = (paper.get("balances") or {}).get("gate_approved", {}).get("equity")
    notes.append(f"paper_status ok equity={eq}")
except Exception as e:
    ok_all = False
    notes.append(f"paper_status FAIL: {e}")

try:
    sessions = get("/api/paper/sessions?limit=5")
    notes.append(f"paper_sessions ok count={sessions.get('count')}")
except Exception as e:
    ok_all = False
    notes.append(f"paper_sessions FAIL: {e}")

try:
    td = get("/api/trading-day/status")
    pick = None
    if isinstance(td.get("pick"), dict):
        pick = td["pick"].get("ticker")
    pick = pick or td.get("ranked_first")
    if pick:
        notes.append(f"trading_day #1={pick}")
    else:
        notes.append("trading_day has no #1 yet (ranks may still be loading)")
except Exception as e:
    notes.append(f"trading_day/status unavailable: {e}")

try:
    ranked = get("/api/screener/ranked")
    rows = ranked.get("rows") or ranked.get("ranked") or ranked.get("items") or []
    if isinstance(rows, list) and rows:
        ranked_n = len(rows)
        notes.append(f"screener/ranked rows={ranked_n}")
        if not pick and isinstance(rows[0], dict):
            pick = rows[0].get("ticker")
    else:
        notes.append("screener/ranked returned no rows (will check DB snapshot)")
except Exception as e:
    notes.append(f"screener/ranked unavailable: {e}")

try:
    db = os.environ.get("DB_PATH") or str(Path("data") / "agent.db")
    if Path(db).is_file():
        conn = sqlite3.connect(db)
        n = conn.execute(
            "SELECT COUNT(*) AS n FROM rank_snapshots WHERE snapshot_date = ?",
            (day,),
        ).fetchone()[0]
        conn.close()
        ranked_n = max(ranked_n, int(n or 0))
        if n > 0:
            notes.append(f"rank_snapshots today={n}")
        else:
            notes.append("rank_snapshots today=0")
    else:
        ok_all = False
        notes.append(f"db missing: {db}")
except Exception as e:
    ok_all = False
    notes.append(f"rank check FAIL: {e}")

if ranked_n <= 0:
    ok_all = False

print("PROOF_OK" if ok_all else "PROOF_FAIL")
for line in notes:
    print(line)
if pick:
    print(f"NUMBER_ONE={pick}")
PY
echo "$PROOF"
if echo "$PROOF" | grep -q '^PROOF_OK'; then
  ok "dashboard has today's ranks + paper status/log APIs"
  if echo "$PROOF" | grep -q '^NUMBER_ONE='; then
    ok "#1 pick: $(echo "$PROOF" | awk -F= '/^NUMBER_ONE=/{print $2}')"
  else
    warn "#1 pick not shown yet — ranks present; open Dashboard Trade/Auto view after refresh"
  fi
else
  bad "dashboard proof failed — ranks/#1/paper log not available (see PROOF lines above)"
fi
echo ""

echo "── Banner notification proof (SMTP not required) ──"
NOTIFY_OUT=$("$ROOT/scripts/run_morning_health_mac.sh" --force-notify 2>&1) || true
echo "$NOTIFY_OUT"
if echo "$NOTIFY_OUT" | grep -qiE 'banner[=:]?\s*True|banner=True'; then
  ok "macOS banner notification fired"
elif echo "$NOTIFY_OUT" | grep -qiE 'Notify: ok=True'; then
  ok "notify path ok (banner may be suppressed by Focus/Do Not Disturb — check Notification Center)"
else
  bad "forced health notify did not report success — see output above"
fi
if echo "$NOTIFY_OUT" | grep -qiE 'emailed[=:]?\s*True|emailed=True'; then
  ok "optional email also sent"
else
  ok "email skipped/not configured — OK"
fi
echo ""

echo "── Doctor ──"
"$ROOT/scripts/doctor_paper_ready_mac.sh" || FAILS=$((FAILS + 1))
echo ""

echo "=== Final ==="
if [[ "$FAILS" -eq 0 ]]; then
  echo "RESULT: READY_UNATTENDED"
  echo "Leave Mac awake on AC (sleep=0)."
  echo "Tomorrow: morning prep builds ranks/#1; paper-worker logs fills on Dashboard."
  echo "Notifications: macOS banners (no SMTP required)."
  exit 0
fi
echo "RESULT: NOT_READY ($FAILS issue(s))"
echo "Do NOT leave until this script prints READY_UNATTENDED."
exit 1
