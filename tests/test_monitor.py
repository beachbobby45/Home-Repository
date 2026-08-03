"""Tests for intraday monitor (Phase 4)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_quote
from investment_agent.monitor import (
    evaluate_queue_item,
    pnl_pct,
    run_monitor_cycle,
    target_stop_prices,
)
from investment_agent.strategy import STOP_PCT, TARGET_PCT


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _queue_row(conn, ticker: str, state: str, entry: float, qid: int = 1):
    target, stop = target_stop_prices(entry)
    conn.execute(
        """
        INSERT INTO queue_items
          (id, ticker, state, entry_price, target_price, stop_price, suggested_size)
        VALUES (?, ?, ?, ?, ?, ?, 10000)
        """,
        (qid, ticker, state, entry, target, stop),
    )
    conn.commit()
    return conn.execute(
        "SELECT id, ticker, state, entry_price, target_price, stop_price FROM queue_items WHERE id = ?",
        (qid,),
    ).fetchone()


def test_target_stop_prices():
    entry = 100.0
    target, stop = target_stop_prices(entry)
    assert abs(target - entry * (1 + TARGET_PCT / 100)) < 0.01
    assert abs(stop - entry * (1 - STOP_PCT / 100)) < 0.01


def test_pnl_pct():
    assert abs(pnl_pct(100, 101.5) - 1.5) < 0.01


def test_target_hit_creates_alert():
    conn, path = _conn()
    try:
        entry = 100.0
        target, stop = target_stop_prices(entry)
        row = _queue_row(conn, "NVDA", "in_trade", entry)
        quotes = {"NVDA": target + 0.10}
        ev = evaluate_queue_item(conn, row, quotes, eod=False)
        assert ev is not None
        assert ev.alert_type == "TARGET_HIT"

        result = run_monitor_cycle(conn, quotes)
        assert result["new_alerts"] == 1
        alert = conn.execute("SELECT alert_type, ticker FROM price_alerts").fetchone()
        assert alert["alert_type"] == "TARGET_HIT"
        assert alert["ticker"] == "NVDA"

        # Idempotent same day
        result2 = run_monitor_cycle(conn, quotes)
        assert result2["new_alerts"] == 0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_stop_hit_creates_alert():
    conn, path = _conn()
    try:
        entry = 500.0
        _, stop = target_stop_prices(entry)
        row = _queue_row(conn, "META", "in_trade", entry)
        quotes = {"META": stop - 0.05}
        ev = evaluate_queue_item(conn, row, quotes, eod=False)
        assert ev is not None
        assert ev.alert_type == "STOP_HIT"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_eod_flatten_alert():
    conn, path = _conn()
    try:
        row = _queue_row(conn, "MSFT", "in_trade", 420.0)
        quotes = {"MSFT": 421.0}
        ev = evaluate_queue_item(conn, row, quotes, eod=True)
        assert ev is not None
        assert ev.alert_type == "EOD_FLATTEN"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_missing_quote_skipped():
    conn, path = _conn()
    try:
        _queue_row(conn, "AMD", "armed", 160.0)
        result = run_monitor_cycle(conn, {})
        assert "AMD" in result["missing_quotes"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)
