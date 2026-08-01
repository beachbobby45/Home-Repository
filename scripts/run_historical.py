#!/usr/bin/env python3
"""Pull limited historical OHLCV and evaluate prior day / date range."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.historical import (
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    pull_historical_data,
)
from investment_agent.ingest import DEFAULT_TICKERS


def main() -> None:
    parser = argparse.ArgumentParser(description="Historical OHLCV pull + day evaluation")
    sub = parser.add_subparsers(dest="command", required=True)

    pull = sub.add_parser("pull", help="Fetch limited daily bars into SQLite")
    pull.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    pull.add_argument("--lookback-days", type=int, default=60)
    pull.add_argument("--db", type=Path, default=None)

    prior = sub.add_parser("prior-day", help="Evaluate prior trading day vs historical view")
    prior.add_argument("--db", type=Path, default=None)

    day = sub.add_parser("evaluate-day", help="Evaluate a specific YYYY-MM-DD")
    day.add_argument("date")
    day.add_argument("--db", type=Path, default=None)

    period = sub.add_parser("period", help="Evaluate each day in a date range")
    period.add_argument("--from", dest="start_date", required=True)
    period.add_argument("--to", dest="end_date", required=True)
    period.add_argument("--db", type=Path, default=None)

    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "pull":
        result = pull_historical_data(
            settings,
            tickers=args.tickers,
            db_path=args.db,
            lookback_days=args.lookback_days,
        )
    elif args.command == "prior-day":
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_prior_day(conn)
            if result is None:
                print(json.dumps({"ok": False, "error": "No historical bars in database — run pull first"}))
                sys.exit(1)
        finally:
            conn.close()
    elif args.command == "evaluate-day":
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_trading_day(conn, args.date)
        finally:
            conn.close()
    else:
        import sqlite3

        from investment_agent.db import connect, init_db

        path = init_db(args.db)
        conn = connect(path)
        try:
            result = evaluate_period(conn, args.start_date, args.end_date)
        finally:
            conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
