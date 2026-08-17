#!/bin/bash
# Diagnose End of Day / ingest failures (missing keys, API reachability, stale lock).
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

echo "=== Ingest doctor ==="
echo "Repo: $ROOT"
echo ""

fail=0
ok() { echo "OK:   $*"; }
bad() { echo "FAIL: $*"; fail=1; }
warn() { echo "WARN: $*"; }

if [[ ! -f "$ROOT/.env" ]]; then
  bad ".env missing — copy from .env.example and add FRED_API_KEY + FINNHUB_API_KEY"
else
  ok ".env exists"
  if grep -qE '^FRED_API_KEY=.+' "$ROOT/.env" 2>/dev/null; then
    ok "FRED_API_KEY set"
  else
    bad "FRED_API_KEY missing or empty in .env"
  fi
  if grep -qE '^FINNHUB_API_KEY=.+' "$ROOT/.env" 2>/dev/null; then
    ok "FINNHUB_API_KEY set"
  else
    bad "FINNHUB_API_KEY missing or empty in .env"
  fi
fi

export PYTHONPATH="$ROOT/src"
if python3 -c "from investment_agent.db_maintenance import clear_stale_ingest_lock; clear_stale_ingest_lock()" 2>/dev/null; then
  :
fi

echo ""
echo "Running preflight (FRED + Finnhub live check, ~5 sec)…"
echo ""
if python3 "$ROOT/scripts/preflight_ingest.py"; then
  ok "Preflight passed"
else
  bad "Preflight failed — see ERROR lines above"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "All checks passed. End of Day Step 1 should start (15–25 min for S&P 500)."
else
  echo "Fix the FAIL items above, then retry End of Day in the Desktop app."
fi
exit "$fail"
