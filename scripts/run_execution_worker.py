#!/usr/bin/env python3
"""Local execution worker (dry-run until Robinhood client is wired).

Phases:
  - sync fixture or live broker snapshot → SQLite mirror
  - print PDT status + today's armed plan
  - never submits orders unless EXECUTION_LIVE=1 and client is configured

Usage:
  PYTHONPATH=src .venv/bin/python3 scripts/run_execution_worker.py --once
  PYTHONPATH=src .venv/bin/python3 scripts/run_execution_worker.py --loop --interval 60
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.broker.client import StubBrokerClient, fixture_paper_snapshot
from investment_agent.broker.sync import latest_broker_balance, sync_from_client
from investment_agent.db import connect, init_db
from investment_agent.execution.armed_plan import get_armed_plan_for_session
from investment_agent.execution.propose import pdt_status_payload
from investment_agent.risk_engine import is_kill_switch_active
from investment_agent.trading_day import today_et_str


def _run_once(conn, *, equity: float, cash: float, account_id: str) -> dict:
    live = os.environ.get("EXECUTION_LIVE", "").strip() in {"1", "true", "yes"}
    if live:
        # Placeholder: real Robinhood client will replace stub when credentials exist.
        print("EXECUTION_LIVE set but Robinhood client not configured — using fixture sync.")
    client = StubBrokerClient(
        fixture_paper_snapshot(equity=equity, cash=cash, account_id=account_id)
    )
    sync = sync_from_client(conn, client)
    conn.commit()
    day = today_et_str()
    pdt = pdt_status_payload(conn, day)
    plan = get_armed_plan_for_session(conn, day)
    paused = is_kill_switch_active(conn)
    bal = latest_broker_balance(conn)
    return {
        "sync": sync,
        "pdt": pdt,
        "plan_status": plan.status.value if plan else None,
        "plan_ticker": plan.legs[0].ticker if plan and plan.legs else None,
        "kill_switch_active": paused,
        "balance": {
            "equity": bal.get("equity") if bal else None,
            "cash": bal.get("cash") if bal else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execution worker (dry-run)")
    parser.add_argument("--once", action="store_true", help="Single sync+status cycle")
    parser.add_argument("--loop", action="store_true", help="Repeat until interrupted")
    parser.add_argument("--interval", type=int, default=60, help="Loop seconds")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--equity", type=float, default=5_000.0)
    parser.add_argument("--cash", type=float, default=5_000.0)
    parser.add_argument("--account-id", default="rh-paper-fixture-001")
    args = parser.parse_args()
    if not args.once and not args.loop:
        args.once = True

    db_path = init_db(args.db)
    conn = connect(db_path)
    try:
        while True:
            result = _run_once(
                conn,
                equity=args.equity,
                cash=args.cash,
                account_id=args.account_id,
            )
            print(
                f"[execution-worker] sync ok equity=${result['sync']['equity']:.2f} "
                f"PDT {result['pdt']['used']}/{result['pdt']['cap']} "
                f"allowed={result['pdt']['allowed']} "
                f"plan={result['plan_status']} {result['plan_ticker'] or '-'} "
                f"kill_switch={result['kill_switch_active']}"
            )
            if args.once or not args.loop:
                break
            time.sleep(max(args.interval, 5))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
