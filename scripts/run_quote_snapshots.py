#!/usr/bin/env python3
"""Capture scheduled intraday quote snapshots (Phase 1B Inc 11).

Stores one row per ticker per slot per ET session day:
  pre_market, at_open (9:30–9:44), plus_15m (9:45–9:59).

Use during the matching window, or pass --slot to force a slot for backfill/testing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import connect, init_db
from investment_agent.quote_snapshots import (
    SNAPSHOT_SLOTS,
    capture_quote_snapshots,
    get_session_snapshot_status,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture intraday quote snapshots")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--slot",
        choices=SNAPSHOT_SLOTS,
        default=None,
        help="Force snapshot slot (default: active window)",
    )
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args()

    settings = Settings.from_env()
    path = init_db(args.db)
    conn = connect(path)
    try:
        result = capture_quote_snapshots(conn, settings, slot=args.slot)
        if result.get("ok"):
            conn.commit()
        status = get_session_snapshot_status(conn)
    finally:
        conn.close()

    if args.json:
        print(json.dumps({"capture": result, "status": status}, indent=2))
        sys.exit(0 if result.get("ok") else 1)

    if not result.get("ok"):
        print(result.get("error") or "Snapshot capture failed")
        sys.exit(1)

    snap = result.get("snapshot") or {}
    updated = result.get("updated") or []
    print(
        f"Snapshot OK — slot {snap.get('slot_label') or snap.get('slot')} · "
        f"{snap.get('tickers', len(updated))} tickers"
    )
    if result.get("errors"):
        print("Errors:")
        for err in result["errors"][:5]:
            print(f"  {err}")
    for slot in status.get("slots") or []:
        mark = "✓" if slot.get("captured") else "·"
        print(f"  {mark} {slot.get('label')} ({slot.get('ticker_count', 0)} tickers)")

    sys.exit(0)


if __name__ == "__main__":
    main()
