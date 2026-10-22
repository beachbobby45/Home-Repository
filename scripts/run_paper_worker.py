#!/usr/bin/env python3
"""Paper ledger worker — no Robinhood. Dual arms: gate_approved + all_signals.

Usage:
  PYTHONPATH=src .venv/bin/python3 scripts/run_paper_worker.py --once
  PYTHONPATH=src .venv/bin/python3 scripts/run_paper_worker.py --loop --interval 60
  PYTHONPATH=src .venv/bin/python3 scripts/run_paper_worker.py --once --force-complete --date 2026-10-17
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.paper_runner import paper_status_payload, run_paper_tick


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper execution worker (no broker)")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--date", type=str, default=None, help="ET session date YYYY-MM-DD")
    parser.add_argument(
        "--force-complete",
        action="store_true",
        help="Treat day as complete (EOD/backfill) using all available 5m bars",
    )
    parser.add_argument("--starting-cash", type=float, default=5_000.0)
    parser.add_argument("--status-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.once and not args.loop and not args.status_only:
        args.once = True

    db_path = init_db(args.db)
    conn = connect(db_path)
    try:
        if args.status_only:
            payload = paper_status_payload(conn)
            if args.json:
                print(json.dumps(payload, indent=2, default=str))
            else:
                sb = payload["scoreboard"]
                print(
                    f"[paper] day={payload['session_date_et']} "
                    f"gate_eq=${payload['balances']['gate_approved']['equity']:.2f} "
                    f"all_eq=${payload['balances']['all_signals']['equity']:.2f} "
                    f"fills={sb['arms']['gate_approved']['fills']} "
                    f"pass={sb['paper_pass']}"
                )
            return 0

        while True:
            result = run_paper_tick(
                conn,
                session_date_et=args.date,
                starting_cash=args.starting_cash,
                force_complete=args.force_complete,
            )
            conn.commit()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                sig = result.get("signal") or {}
                bal = result.get("balances") or {}
                g = bal.get("gate_approved") or {}
                a = bal.get("all_signals") or {}
                print(
                    f"[paper-worker] {result.get('session_date_et')} "
                    f"ticker={sig.get('ticker') or '-'} "
                    f"allow_trade={sig.get('allow_trade')} "
                    f"gate_eq=${float(g.get('equity') or 0):.2f} "
                    f"all_eq=${float(a.get('equity') or 0):.2f} "
                    f"ok={result.get('ok')}"
                )
            if args.once or not args.loop:
                break
            time.sleep(max(args.interval, 15))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
