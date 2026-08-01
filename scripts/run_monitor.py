#!/usr/bin/env python3
"""Run one intraday monitor cycle (+1.13% / −0.50% alerts)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import connect, init_db, insert_quote
from investment_agent.monitor import run_monitor_cycle, utc_now_iso
from investment_agent.providers.finnhub import FinnhubClient


def _refresh_quotes(conn, tickers: list[str], api_key: str) -> int:
    fh = FinnhubClient(api_key)
    count = 0
    try:
        for symbol in tickers:
            try:
                q = fh.get_quote(symbol)
                insert_quote(
                    conn,
                    {
                        "ticker": symbol,
                        "captured_at": utc_now_iso(),
                        "price": float(q["c"]),
                        "open": float(q.get("o") or 0) or None,
                        "high": float(q.get("h") or 0) or None,
                        "low": float(q.get("l") or 0) or None,
                        "prev_close": float(q.get("pc") or 0) or None,
                    },
                )
                count += 1
            except Exception as exc:
                print(f"WARN: quote {symbol}: {exc}", file=sys.stderr)
    finally:
        fh.close()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Run intraday monitor cycle")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--refresh-quotes",
        action="store_true",
        help="Fetch live Finnhub quotes for monitored tickers first",
    )
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        if args.refresh_quotes:
            settings = Settings.from_env()
            if not settings.finnhub_api_key:
                print("ERROR: FINNHUB_API_KEY required for --refresh-quotes")
                sys.exit(2)
            rows = conn.execute(
                """
                SELECT DISTINCT ticker FROM queue_items
                WHERE state IN ('armed','alert','in_trade','eod')
                """
            ).fetchall()
            tickers = [r[0] for r in rows]
            updated = _refresh_quotes(conn, tickers, settings.finnhub_api_key)
            print(f"Refreshed {updated} quote(s)", file=sys.stderr)

        result = run_monitor_cycle(conn)
        conn.commit()

    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
