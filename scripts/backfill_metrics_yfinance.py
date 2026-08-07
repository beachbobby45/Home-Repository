#!/usr/bin/env python3
"""Backfill ticker_metrics from yfinance daily bars (no Finnhub required)."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db, get_active_watchlist, insert_ticker_metrics
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.yfinance_bars import get_daily_bars


def main() -> int:
    init_db()
    conn = connect()
    symbols = get_active_watchlist(conn)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ok, err = 0, 0
    for i, sym in enumerate(symbols, 1):
        try:
            candles = get_daily_bars(sym, lookback_days=60)
            bars = [
                DailyBar(high=r["high"], low=r["low"], close=r["close"], volume=r["volume"])
                for r in sorted(candles, key=lambda x: x["date"])
            ]
            m = compute_liquidity_metrics(bars, tradable_cash=ORIGINAL_BASIS)
            last_close = bars[-1].close if bars else 0.0
            insert_ticker_metrics(
                conn,
                {
                    "ticker": sym,
                    "computed_at": now,
                    "adv_dollar": m.adv_dollar,
                    "avg_range_pct": m.avg_range_pct,
                    "liquidity_cap": m.liquidity_cap,
                    "last_close": last_close,
                    "last_quote": last_close,
                    "meets_liquidity_min": m.meets_liquidity_min,
                    "near_swing_target": m.near_swing_target,
                },
            )
            ok += 1
        except Exception as exc:
            err += 1
            print(f"ERR {sym}: {exc}", file=sys.stderr)
        if i % 25 == 0:
            conn.commit()
            print(f"... {i}/{len(symbols)} ok={ok} err={err}", flush=True)
    conn.commit()
    conn.close()
    print(f"DONE ok={ok} err={err} total={len(symbols)}")
    return 0 if err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
