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

chmod +x "$ROOT/scripts/resolve_python.sh" 2>/dev/null || true
if PY="$("$ROOT/scripts/resolve_python.sh" 2>/dev/null)"; then
  ok "ingest/dashboard Python: $PY ($("$PY" --version 2>&1))"
else
  bad "no working .venv Python — run: ./scripts/fix_ingest_python_mac.sh"
  PY=""
fi

if [[ -n "$PY" ]]; then
  for mod in uvicorn fastapi jinja2 dotenv; do
    if "$PY" -c "import $mod" 2>/dev/null; then
      ok "import $mod"
    else
      bad "missing '$mod' — run: ./scripts/fix_ingest_python_mac.sh"
    fi
  done
  if PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.dashboard.app import app" 2>/dev/null; then
    ok "dashboard app imports"
  else
    bad "dashboard app failed to import:"
    PYTHONPATH="$ROOT/src" "$PY" -c "from investment_agent.dashboard.app import app" 2>&1 | tail -5
  fi
fi

if [[ -f "$HOME/Library/LaunchAgents/com.investment-agent.dashboard.plist" ]]; then
  ok "LaunchAgent plist installed"
else
  warn "no LaunchAgent — dashboard starts via Open Dashboard.command or ensure_dashboard_mac.sh"
fi

if command -v lsof >/dev/null 2>&1; then
  if lsof -ti:8080 >/dev/null 2>&1; then
    ok "something listening on port 8080"
  else
    warn "nothing on port 8080 — run: ./scripts/ensure_dashboard_mac.sh"
  fi
fi

CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 "$URL/api/version" 2>/dev/null || echo "000")
if [[ "$CODE" == "200" ]]; then
  ok "dashboard responds HTTP 200 at $URL"
else
  bad "dashboard not responding (HTTP $CODE) — run: ./scripts/ensure_dashboard_mac.sh"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "Dashboard looks healthy. Open: $URL"
else
  echo "Fix FAIL items above, then: ./scripts/ensure_dashboard_mac.sh"
fi
exit "$fail"
