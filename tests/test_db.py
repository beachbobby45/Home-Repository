"""Tests for database init."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, upsert_watchlist


def test_init_db_creates_tables():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.db"
        init_db(path)
        conn = sqlite3.connect(path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        assert "watchlist" in tables
        assert "ohlcv_daily" in tables
        assert "ticker_metrics" in tables
        assert "regime_snapshots" in tables
        assert "queue_items" in tables
        assert "trade_journal" in tables
        assert "price_alerts" in tables
        assert "learning_reports" in tables
        assert "news_headlines" in tables
        assert "trade_proposals" in tables


def test_upsert_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.db"
        init_db(path)
        conn = sqlite3.connect(path)
        upsert_watchlist(conn, ["SPY", "AAPL"])
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
        conn.close()
        assert count == 2
