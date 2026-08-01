"""Tests for stock team screener and queue."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ticker_metrics
from investment_agent.stock_team import (
    advance_queue_state,
    build_analysis_card,
    sync_queue_from_screener,
)


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _insert_metric(conn, ticker: str, *, near_swing: bool = True):
    insert_ticker_metrics(
        conn,
        {
            "ticker": ticker,
            "computed_at": "2026-07-31T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0 if near_swing else 1.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": near_swing,
        },
    )


def test_build_analysis_card_excludes_spy():
    conn, path = _conn()
    try:
        _insert_metric(conn, "SPY")
        conn.commit()
        row = conn.execute("SELECT * FROM ticker_metrics LIMIT 1").fetchone()
        assert build_analysis_card(row, 10_000) is None
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_sync_queue_adds_candidates():
    conn, path = _conn()
    try:
        _insert_metric(conn, "AAPL")
        _insert_metric(conn, "MSFT", near_swing=False)
        conn.commit()
        result = sync_queue_from_screener(conn, max_items=3)
        assert result["ok"] is True
        assert result["added"] == 1
        assert result["added_tickers"] == ["AAPL"]
        row = conn.execute("SELECT ticker, state FROM queue_items").fetchone()
        assert row["ticker"] == "AAPL"
        assert row["state"] == "watching"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_sync_queue_skips_when_all_live_already_active():
    conn, path = _conn()
    try:
        _insert_metric(conn, "AAPL")
        conn.commit()
        first = sync_queue_from_screener(conn, max_items=3)
        assert first["added"] == 1
        second = sync_queue_from_screener(conn, max_items=3)
        assert second["added"] == 0
        assert second["already_in_queue"] == 1
        assert "already in the queue" in second["message"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_advance_queue_state():
    conn, path = _conn()
    try:
        conn.execute(
            """
            INSERT INTO queue_items (ticker, state, entry_price, target_price, stop_price)
            VALUES ('AAPL', 'watching', 100, 101.13, 99.5)
            """
        )
        conn.commit()
        result = advance_queue_state(conn, 1)
        assert result["ok"] is True
        assert result["to_state"] == "approved"
    finally:
        conn.close()
        path.unlink(missing_ok=True)
