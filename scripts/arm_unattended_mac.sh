#!/bin/bash
# Arm the Mac for unattended paper days. Installs schedules, proves health email,
# and exits non-zero unless READY. Run this ONCE before you leave the machine.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/arm_unattended_mac.sh
#   ./scripts/arm_unattended_mac.sh --no-pull
#
# READY means: paper-worker + dashboard + morning_prep + morning health LaunchAgents
# are loaded, sleep=0, SMTP can send, and a forced health email was attempted successfully.

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
  "$ROOT/scripts/install_dashboard_service_mac.sh" \
  2>/dev/null || true

if [[ ! -f "$ROOT/.env" ]]; then
  bad ".env missing — copy .env.example and set FINNHUB + SMTP before arming"
  echo "RESULT: NOT_READY"
  exit 1
fi

# SMTP must be present for unattended email proof
# shellcheck disable=SC1091
set -a
# shellcheck disable=SC1090
source "$ROOT/.env" 2>/dev/null || true
set +a
if [[ -z "${SMTP_HOST:-}" || -z "${SMTP_USER:-}" || -z "${SMTP_PASSWORD:-}" ]]; then
  bad "SMTP_HOST / SMTP_USER / SMTP_PASSWORD not set in .env — morning email will not reach you while away"
else
  ok "SMTP_* present in .env"
fi
if [[ "${NOTIFY_ENABLED:-1}" == "0" ]]; then
  bad "NOTIFY_ENABLED=0 — turn on for unattended health/paper emails"
else
  ok "NOTIFY_ENABLED on"
fi

# Timezone → schedule flavor
TZ_NAME=$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||' || true)
PACIFIC_FLAG=""
HEALTH_FLAG=""
case "${TZ_NAME:-}" in
  America/Los_Angeles|US/Pacific|PST|PDT)
    PACIFIC_FLAG="--pacific"
    HEALTH_FLAG=""  # morning health defaults to Pacific
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
if [[ -x "$ROOT/scripts/install_dashboard_service_mac.sh" ]]; then
  "$ROOT/scripts/install_dashboard_service_mac.sh" || bad "dashboard service install failed"
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
# midmorning is optional but preferred
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
    echo "      Without this, calendar jobs (morning prep / health) often miss while you are away."
  fi
else
  bad "pmset unavailable"
fi
echo ""

echo "── Force health email proof (must succeed before you leave) ──"
NOTIFY_OUT=$("$ROOT/scripts/run_morning_health_mac.sh" --force-notify 2>&1) || true
echo "$NOTIFY_OUT"
if echo "$NOTIFY_OUT" | grep -qiE 'emailed[=:]?\s*True|emailed=True'; then
  ok "health email reported emailed=True — check inbox/spam for Beachbobby45@att.net"
elif echo "$NOTIFY_OUT" | grep -qiE 'Notify: ok=True'; then
  # banner-only path still not enough when away
  if echo "$NOTIFY_OUT" | grep -qiE 'emailed[=:]?\s*False|emailed=False|SMTP|smtp'; then
    bad "health ran but email did not send — fix SMTP_* in .env and re-run this script"
  else
    warn "health notify ok but emailed flag unclear — check inbox and ~/Library/Logs/investment-agent/"
  fi
else
  bad "forced health notify did not report success — see output above"
fi
echo ""

echo "── Doctor ──"
"$ROOT/scripts/doctor_paper_ready_mac.sh" || FAILS=$((FAILS + 1))
echo ""

echo "=== Final ==="
if [[ "$FAILS" -eq 0 ]]; then
  echo "RESULT: READY_UNATTENDED"
  echo "Leave Mac awake on AC (sleep=0). Tomorrow you should get morning health email(s)."
  echo "Paper buy/sell emails fire only if a simulated fill happens that day."
  exit 0
fi
echo "RESULT: NOT_READY ($FAILS issue(s))"
echo "Do NOT leave until this script prints READY_UNATTENDED."
exit 1
