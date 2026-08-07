"""Tests for daily dollar backtest."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import run_dollar_daily_backtest
from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics, upsert_watchlist


def _seed(conn, eval_date: str):
    upsert_watchlist(conn, ["AAPL"])
    insert_ticker_metrics(
        conn,
        {
            "ticker": "AAPL",
            "computed_at": "2026-08-01T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": True,
        },
    )
    end = datetime.strptime(eval_date, "%Y-%m-%d")
    rows = []
    for offset in range(10, 0, -1):
        day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
        close = 100.0
        open_px = 100.0
        high = 102.5 if day == eval_date else 101.2
        low = 99.2
        rows.append(
            {
                "ticker": "AAPL",
                "date": day,
                "open": open_px,
                "high": high,
                "low": low,
                "close": close,
                "volume": 10_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def test_dollar_daily_backtest_runs():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bt.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()
        result = run_dollar_daily_backtest(conn, lookback_days=14, starting_capital=10_000)
        conn.close()
        assert result["total_trades"] >= 0
        assert "dollar_hit_rate_pct" in result
        assert result["assumptions"]
