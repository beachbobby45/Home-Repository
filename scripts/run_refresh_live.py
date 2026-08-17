#!/usr/bin/env python3
"""Refresh live Finnhub quotes and print go/no-go for Step 3 (before buy or sell)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import connect, init_db
from investment_agent.screen_actions import ACTION_REFRESH_LIVE, record_screen_action
from investment_agent.trading_day import build_trading_day_status, refresh_live_quotes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 3 — refresh live quotes before placing limit orders in E*TRADE"
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print full JSON status")
    args = parser.parse_args()

    settings = Settings.from_env()
    if not settings.finnhub_api_key:
        print("ERROR: FINNHUB_API_KEY required in .env")
        sys.exit(2)

    path = init_db(args.db)
    conn = connect(path)
    try:
        refresh = refresh_live_quotes(conn, settings)
        if not refresh.get("ok"):
            print(refresh.get("error") or "Refresh failed")
            sys.exit(1)
        n = len(refresh.get("updated") or [])
        record_screen_action(conn, ACTION_REFRESH_LIVE, detail=f"Step 3 · {n} symbols updated")
        conn.commit()
        status = build_trading_day_status(conn)
    finally:
        conn.close()

    if args.json:
        print(json.dumps({"refresh": refresh, "status": status}, indent=2))
        sys.exit(0)

    updated = refresh.get("updated") or []
    print(f"Live refresh OK — {len(updated)} symbols updated")
    print(f"Verdict: {status.get('verdict')} — {status.get('headline')}")
    if status.get("detail"):
        print(f"Detail: {status['detail']}")

    pick = status.get("top_pick")
    if pick:
        limit_buy = pick.get("limit_buy_price") or pick.get("entry_price")
        limit_sell = pick.get("limit_sell_price") or pick.get("target_price")
        print(
            f"\n#1 {pick['ticker']}: limit buy ${limit_buy:.2f} · "
            f"limit sell ${limit_sell:.2f} · stop ${pick.get('stop_price', 0):.2f}"
        )
        if pick.get("pullback_pct") is not None:
            print(
                f"   Open ${pick.get('session_open', 0):.2f} · "
                f"pullback −{pick['pullback_pct']}% · cancel unfilled by 11:30 ET"
            )
    else:
        print("\nNo tradable #1 pick for today's dollar goal.")
        skipped = status.get("skipped_not_tradable") or []
        if skipped:
            print("Skipped:")
            for row in skipped[:5]:
                print(f"  {row.get('ticker')}: {row.get('reason', row.get('verdict'))}")

    sys.exit(0 if status.get("verdict") in ("GO", "CAUTION", "WAIT") else 1)


if __name__ == "__main__":
    main()
