#!/usr/bin/env python3
"""Manage watchlist presets and imports (Phase 7)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.watchlist import (
    compute_universe_stats,
    deactivate_ticker,
    get_active_watchlist_details,
    import_tickers,
    list_presets,
    load_preset_into_watchlist,
    load_tickers_from_file,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Watchlist manager")
    parser.add_argument("--db", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("presets", help="List available presets")

    load = sub.add_parser("load-preset", help="Load a preset into active watchlist")
    load.add_argument("name", choices=["starter10", "sp100"])
    load.add_argument(
        "--replace",
        action="store_true",
        help="Deactivate all tickers before loading preset",
    )

    imp = sub.add_parser("import", help="Import tickers from file")
    imp.add_argument("--file", type=Path, required=True)

    sub.add_parser("list", help="List active watchlist tickers")
    sub.add_parser("stats", help="Universe Step 3 pass/filter stats")

    rm = sub.add_parser("remove", help="Deactivate a ticker")
    rm.add_argument("ticker")

    args = parser.parse_args()
    path = init_db(args.db)
    conn = connect(path)

    try:
        if args.command == "presets":
            result = [
                {
                    "name": p.name,
                    "description": p.description,
                    "ticker_count": p.ticker_count,
                }
                for p in list_presets()
            ]
        elif args.command == "load-preset":
            result = load_preset_into_watchlist(conn, args.name, replace=args.replace)
            conn.commit()
        elif args.command == "import":
            tickers = load_tickers_from_file(args.file)
            result = import_tickers(conn, tickers, added_via=str(args.file))
            conn.commit()
        elif args.command == "list":
            result = {"tickers": get_active_watchlist_details(conn)}
        elif args.command == "stats":
            result = compute_universe_stats(conn)
        elif args.command == "remove":
            result = deactivate_ticker(conn, args.ticker)
            conn.commit()
        else:
            result = {"ok": False, "error": "unknown command"}
    finally:
        conn.close()

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
