#!/usr/bin/env python3
"""Random-pick control vs #1 ranked — same fees/entry/exit/fill_mode as paper_sim.

Usage:
  PYTHONPATH=src .venv/bin/python3 scripts/run_random_pick_control.py
  PYTHONPATH=src .venv/bin/python3 scripts/run_random_pick_control.py \\
      --since 2026-10-20 --top-n 20 --fill-mode trade_through --seed 42
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db  # noqa: E402
from investment_agent.execution.random_control import run_random_pick_control  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Random-pick control for paper scoreboard")
    p.add_argument("--since", default="2026-10-20")
    p.add_argument("--until", default=None)
    p.add_argument("--top-n", type=int, default=20)
    p.add_argument("--deploy", type=float, default=5_000.0)
    p.add_argument("--fill-mode", default=None, help="touch|trade_through (default: env/PAPER_FILL_MODE)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--lookback-days", type=int, default=60)
    p.add_argument("--no-persist", action="store_true")
    p.add_argument("--json", action="store_true", help="Print full JSON including day rows")
    args = p.parse_args()

    conn = connect(init_db())
    try:
        summary = run_random_pick_control(
            conn,
            since=args.since,
            until=args.until,
            top_n=args.top_n,
            deploy=args.deploy,
            fill_mode=args.fill_mode,
            seed=args.seed,
            lookback_days=args.lookback_days,
            persist=not args.no_persist,
        )
        conn.commit()
        if args.json:
            print(json.dumps(summary, indent=2, default=str))
        else:
            compact = {k: v for k, v in summary.items() if k != "days"}
            print(json.dumps(compact, indent=2, default=str))
            print("")
            beats = summary.get("beats_random")
            if beats is True:
                print("Result: #1 ranked BEATS random control (expectancy).")
            elif beats is False:
                print("Result: #1 ranked does NOT beat random control.")
            else:
                print("Result: inconclusive (need comparable sessions on both arms).")
            if not args.no_persist:
                print("Persisted to app_settings key paper_random_control_summary")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
