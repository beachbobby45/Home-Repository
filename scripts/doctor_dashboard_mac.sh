#!/bin/bash
# Diagnose why http://127.0.0.1:8080 won't open (Mac).
# Usage: ./scripts/doctor_dashboard_mac.sh

set -u
cd "$(dirname "$0")/.."
ROOT="$PWD"
URL="http://127.0.0.1:8080"

echo "=== Dashboard doctor ==="
echo "Repo: $ROOT"
echo ""

fail=0
warn() { echo "WARN: $*"; }
ok() { echo "OK:   $*"; }
bad() { echo "FAIL: $*"; fail=1; }

# 1. Python
if command -v python3 >/dev/null 2>&1; then
  ok "python3 at $(command -v python3) — $(python3 --version 2>&1)"
else
  bad "python3 not found — install Python 3 from python.org or: brew install python"
fi

# 2. Dependencies
for mod in uvicorn fastapi jinja2 dotenv; do
  if python3 -c "import $mod" 2>/dev/null; then
    ok "import $mod"
  else
    bad "missing Python module '$mod' — run: pip3 install -r requirements.txt"
  fi
done

# 3. App import
if PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
  ok "dashboard app imports"
else
  bad "dashboard app failed to import:"
  PYTHONPATH="$ROOT/src" python3 -c "from investment_agent.dashboard.app import app" 2>&1 | tail -5
fi

# 4. .env / db
[[ -f "$ROOT/.env" ]] && ok ".env exists" || warn ".env missing (will be created on start)"
[[ -f "$ROOT/data/agent.db" ]] && ok "data/agent.db exists" || warn "data/agent.db missing (will be seeded on start)"

# 5. Port 8080
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:8080 2>/dev/null || true)
  if [[ -n "$PIDS" ]]; then
    ok "port 8080 in use by PID(s): $PIDS"
    CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 "$URL/api/config" 2>/dev/null || echo "000")
    if [[ "$CODE" == "200" ]]; then
      ok "server responds HTTP 200 at $URL"
    else
      bad "port 8080 busy but server returned HTTP $CODE (not our dashboard?)"
    fi
  else
    bad "nothing listening on port 8080 — dashboard is NOT running"
    echo "      Fix: ./scripts/hard_restart_dashboard_mac.sh"
  fi
else
  warn "lsof not available — cannot check port 8080"
fi

# 6. Recent log
LOG="$ROOT/data/dashboard.log"
if [[ -f "$LOG" ]]; then
  echo ""
  echo "--- Last 15 lines of data/dashboard.log ---"
  tail -15 "$LOG"
else
  warn "no data/dashboard.log yet — server may never have been started"
fi

echo ""
if [[ $fail -eq 0 ]]; then
  echo "All checks passed. Open: $URL"
else
  echo "Fix the FAIL items above, then run:"
  echo "  ./scripts/hard_restart_dashboard_mac.sh"
fi
exit $fail
