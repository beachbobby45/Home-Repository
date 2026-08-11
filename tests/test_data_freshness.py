"""Tests for data freshness reporting."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.db import init_db, insert_quote, insert_ticker_metrics, upsert_watchlist
from investment_agent.watchlist import compute_data_freshness


def test_compute_data_freshness_reports_ages():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fresh.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        upsert_watchlist(conn, ["AAPL", "MSFT"])
        insert_quote(
            conn,
            {
                "ticker": "AAPL",
                "captured_at": "2026-08-10T10:00:00+00:00",
                "price": 100.0,
                "open": 99.0,
                "high": 101.0,
                "low": 98.0,
                "prev_close": 99.5,
            },
        )
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": "2026-08-10T10:00:00+00:00",
                "adv_dollar": 1e9,
                "avg_range_pct": 3.0,
                "liquidity_cap": 1e6,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        conn.commit()
        fresh = compute_data_freshness(conn)
        conn.close()
        assert fresh["tickers_with_quotes"] == 1
        assert fresh["tickers_with_metrics"] == 1
        assert fresh["quotes_max_age_hours"] is not None
        assert fresh["quotes_max_age_hours"] > 0
