#!/bin/bash
# Repair virgin paper books to $5,000 settled cash when there are no fills.
# Also forces ledger_source=paper so risk uses the paper book (not $0 journal).
#
# Usage:
#   cd ~/Home-Repository
#   ./scripts/repair_paper_cash_mac.sh
#   ./scripts/repair_paper_cash_mac.sh --force   # reset cash even if already non-zero (still refuses if fills exist)

set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

FORCE=0
PURGE_EVAL=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --purge-eval-sim|--purge-2099) PURGE_EVAL=1 ;;
  esac
done

if [[ "$PURGE_EVAL" -eq 1 ]]; then
  echo "=== Purge eval SIM/2099 pollution from live paper ledger ==="
  "$PY" - <<'PY'
import json
from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import purge_eval_sim_pollution

conn = connect(init_db())
out = purge_eval_sim_pollution(conn)
conn.commit()
print(json.dumps(out, indent=2, default=str))
conn.close()
PY
else
  echo "=== Repair paper cash (starting \$5,000 when no fills) ==="
  echo "(If diagnose showed from=2099-01-02 / ticker SIM, re-run with: --purge-eval-sim)"
  "$PY" - <<PY
import json
from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import repair_virgin_paper_cash

conn = connect(init_db())
out = repair_virgin_paper_cash(conn, force=bool($FORCE))
conn.commit()
print(json.dumps(out, indent=2, default=str))
conn.close()
PY
fi

echo ""
echo "=== Paper status (risk cash base) ==="
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
echo "Done. Risk 1% cap should be ~\$50 on a \$5k settled book."
echo "Refresh Dashboard Account / Auto tabs."
