#!/usr/bin/env python3
"""Run period screener over date range (Phase 7)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.period_screener import (
    date_range_for_period,
    run_period_screener,
    save_screener_run,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Period screener — historical Step 3 aggregation")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--days", type=int, default=14, help="Lookback days (default 14)")
    parser.add_argument("--from", dest="start_date", default=None)
    parser.add_argument("--to", dest="end_date", default=None)
    parser.add_argument("--min-days", type=int, default=1)
    parser.add_argument("--min-hit-rate", type=float, default=None)
    parser.add_argument("--save", action="store_true", help="Persist run to screener_runs")
    args = parser.parse_args()

    path = init_db(args.db)
    conn = connect(path)
    try:
        if args.start_date and args.end_date:
            start, end = args.start_date, args.end_date
        else:
            start, end = date_range_for_period(args.days)

        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end,
            min_days_screened=args.min_days,
            min_hit_rate_pct=args.min_hit_rate,
        )
        if args.save:
            run_id = save_screener_run(conn, result)
            conn.commit()
            result["saved_run_id"] = run_id
    finally:
        conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
