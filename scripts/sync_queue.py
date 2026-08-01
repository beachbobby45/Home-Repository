#!/usr/bin/env python3
"""Sync trade queue from stock team screener (Phase 2 → queue)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.stock_team import sync_queue_from_screener


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync queue from liquidity screener")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()

    path = init_db(args.db)
    with connect(path) as conn:
        result = sync_queue_from_screener(conn)
        conn.commit()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
