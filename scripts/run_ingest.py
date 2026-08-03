#!/usr/bin/env python3
"""Run Phase 1 data ingestion (FRED + Finnhub quotes + yfinance bars). No Claude."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.ingest import DEFAULT_TICKERS, run_ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 ingest — macro, quotes, metrics")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Symbols to ingest (default: all active watchlist symbols)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="SQLite path (default: data/agent.db)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=60,
        help="Daily history window (default: 60)",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Skip symbols with fresh quotes/bars (default: full refresh)",
    )
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=20.0,
        help="Age threshold for incremental mode (default: 20)",
    )
    args = parser.parse_args()

    settings = Settings.from_env()
    if not settings.fred_api_key or not settings.finnhub_api_key:
        print("ERROR: FRED_API_KEY and FINNHUB_API_KEY required in .env")
        sys.exit(2)

    summary = run_ingest(
        settings,
        tickers=args.tickers,
        db_path=args.db,
        lookback_days=args.lookback_days,
        incremental=args.incremental,
        stale_hours=args.stale_hours,
    )
    print(json.dumps(summary, indent=2))
    sys.exit(0 if summary.get("ok") else 1)


if __name__ == "__main__":
    main()
