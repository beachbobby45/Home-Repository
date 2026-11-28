#!/bin/bash
# Scale both paper books to $15,000 equity WITHOUT wiping Oct–Nov history.
# Credits settled cash only (idempotent). Does NOT flip Paper→Live.
#
# Usage:
#   cd ~/Home-Repository
#   git pull   # onto the branch that has this script
#   ./scripts/scale_paper_to_15k_mac.sh
#
# Afterward: restart dashboard / paper-worker if needed, refresh Account tab.
# Risk 1% cap should be ~$150 on a $15k settled book. Daily net target ~$225.

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

TARGET="${1:-15000}"

echo "=== Scale paper books to \$${TARGET} (preserve fills) ==="
"$PY" - <<PY
import json
from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import (
    PAPER_STARTING_CASH,
    top_up_paper_books_to_target,
)

conn = connect(init_db())
out = top_up_paper_books_to_target(conn, target_equity=float($TARGET))
conn.commit()
print(json.dumps(out, indent=2, default=str))
print("configured_PAPER_STARTING_CASH=", PAPER_STARTING_CASH)
conn.close()
PY

echo ""
echo "=== Paper status ==="
curl -s --connect-timeout 3 http://127.0.0.1:8080/api/paper/status | "$PY" -c "
import sys, json
try:
    d = json.load(sys.stdin)
except Exception as e:
    print('dashboard not reachable:', e)
    raise SystemExit(0)
print('allocation_mode=', d.get('allocation_mode'))
for k, v in (d.get('balances') or {}).items():
    print(k, 'settled=', v.get('settled_cash'), 'unsettled=', v.get('unsettled_cash'), 'equity=', v.get('equity'))
" 2>/dev/null || echo "(start dashboard to verify via API)"

echo ""
echo "Done. Mode stays paper. Do NOT flip to Live until 2027-01-04 written go."
echo "Refresh Dashboard Account / Auto / Plan tabs."
echo "Risk 1% cap should be ~\$150 on a \$15k settled book; daily net target ~\$225."
