#!/bin/bash
# Show why paper settled cash may be low (unsettled T+1) and settle if due.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(cd "$PWD" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/_resolve_python_env.sh" 2>/dev/null || true
PY="${PY:-$ROOT/.venv/bin/python3}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONNOUSERSITE=1

"$PY" - <<'PY'
from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import (
    PAPER_ACCOUNTS,
    get_paper_balance,
    settle_due_cash,
)
from investment_agent.trading_day import today_et_str

conn = connect(init_db())
day = today_et_str()
print(f"session_date_et={day}")
print()
print("=== Balances BEFORE settle pass ===")
for name in PAPER_ACCOUNTS:
    b = get_paper_balance(conn, name)
    print(
        f"{name}: settled={b['settled_cash']:.2f} "
        f"unsettled={b['unsettled_cash']:.2f} equity={b['equity']:.2f}"
    )

print()
print("=== Open unsettled rows ===")
rows = conn.execute(
    """
    SELECT account_name, amount, from_session_date_et, settle_on_et, created_at
    FROM paper_unsettled
    WHERE settled_at IS NULL
    ORDER BY settle_on_et, account_name
    """
).fetchall()
if not rows:
    print("(none)")
else:
    for r in rows:
        print(
            f"{r['account_name']}: ${float(r['amount']):.2f} "
            f"from={r['from_session_date_et']} settle_on={r['settle_on_et']}"
        )

print()
print("=== Recent buy fills ===")
fills = conn.execute(
    """
    SELECT account_name, session_date_et, ticker, qty, price, filled_at
    FROM paper_fills
    WHERE side = 'buy'
    ORDER BY filled_at DESC
    LIMIT 8
    """
).fetchall()
if not fills:
    print("(none)")
else:
    for f in fills:
        print(
            f"{f['account_name']} {f['session_date_et']} {f['ticker']} "
            f"{f['qty']} @ {f['price']}  {f['filled_at']}"
        )

moved = settle_due_cash(conn, session_date_et=day)
conn.commit()
print()
print("=== settle_due_cash moved ===", moved)
print("=== Balances AFTER settle pass ===")
for name in PAPER_ACCOUNTS:
    b = get_paper_balance(conn, name)
    print(
        f"{name}: settled={b['settled_cash']:.2f} "
        f"unsettled={b['unsettled_cash']:.2f} equity={b['equity']:.2f}"
    )
    print(f"  → 1% risk cap ≈ ${float(b['settled_cash']) * 0.01:.2f}")
conn.close()
PY
