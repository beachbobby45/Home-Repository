#!/bin/bash
# Diagnose End of Day / ingest failures (missing keys, API reachability, stale lock).
set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"
chmod +x "$ROOT/scripts/resolve_python.sh" "$ROOT/scripts/fix_ingest_python_mac.sh" 2>/dev/null || true

echo "=== Ingest doctor ==="
echo "Repo: $ROOT"
echo ""

fail=0
ok() { echo "OK:   $*"; }
bad() { echo "FAIL: $*"; fail=1; }
warn() { echo "WARN: $*"; }

if ! PY="$("$ROOT/scripts/resolve_python.sh")"; then
  bad "No working ingest Python — run: ./scripts/fix_ingest_python_mac.sh"
  exit 1
fi
ok "Ingest Python: $PY ($("$PY" --version 2>&1))"

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
"$PY" -c "from investment_agent.db_maintenance import clear_stale_ingest_lock; clear_stale_ingest_lock()" 2>/dev/null || true

echo ""
echo "Running preflight (FRED + Finnhub live check, ~5 sec)…"
echo ""
if "$PY" "$ROOT/scripts/preflight_ingest.py"; then
  ok "Preflight passed"
else
  bad "Preflight failed — see ERROR lines above"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "All checks passed. End of Day Step 1 should start (15–25 min for S&P 500)."
else
  echo "Fix the FAIL items above, then retry End of Day in the Desktop app."
  if [[ -f "$ROOT/data/ingest_last_error.txt" ]]; then
    echo ""
    echo "Last ingest error on disk:"
    cat "$ROOT/data/ingest_last_error.txt"
  fi
fi
exit "$fail"
