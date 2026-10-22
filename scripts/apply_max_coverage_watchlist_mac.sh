#!/bin/bash
# Activate max-coverage watchlist: S&P 500 + unique datacenter_us names.
# Then run a full ingest + period screener so ranks rebuild on the wider universe.
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/apply_max_coverage_watchlist_mac.sh

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

echo "=== Apply max-coverage watchlist (sp500_datacenter) ==="
"$PY" "$ROOT/scripts/manage_watchlist.py" load-preset sp500_datacenter --replace

echo ""
echo "=== Active count / breakdown ==="
"$PY" - <<'PY'
from investment_agent.db import connect, init_db, get_active_watchlist
from investment_agent.watchlist import max_coverage_breakdown

conn = connect(init_db())
active = get_active_watchlist(conn)
b = max_coverage_breakdown()
print(f"active_watchlist_count={len(active)}")
print(
    f"preset_union={b['union_count']} "
    f"(sp500={b['sp500_count']} + datacenter_only={b['datacenter_only_count']})"
)
print(f"datacenter_only_sample={b['datacenter_only_sample']}")
conn.close()
PY

echo ""
echo "=== Full ingest (quotes + daily bars for new names) — may take 15–30+ min ==="
echo "(Skip with: SKIP_INGEST=1 ./scripts/apply_max_coverage_watchlist_mac.sh)"
if [[ "${SKIP_INGEST:-0}" != "1" ]]; then
  if [[ -x "$ROOT/scripts/run_ingest_mac.sh" ]]; then
    "$ROOT/scripts/run_ingest_mac.sh" || true
  else
    "$PY" "$ROOT/scripts/run_ingest.py" || true
  fi
else
  echo "SKIP_INGEST=1 — watchlist updated only; run ingest/screener before next session."
fi

echo ""
echo "=== Period screener (rebuild ranks) ==="
if [[ "${SKIP_INGEST:-0}" != "1" ]]; then
  if [[ -f "$ROOT/scripts/run_period_screener.py" ]]; then
    "$PY" "$ROOT/scripts/run_period_screener.py" || true
  fi
fi

echo ""
echo "Done. Dashboard Top 10 / paper top-3 will use this wider universe after ranks refresh."
echo "Verify:  curl -s http://127.0.0.1:8080/api/watchlist | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('count'))\""
