"""Tests for Opening Drive early-entry scoring."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows
from investment_agent.opening_drive import (
    OPENING_DRIVE_PASS_MIN,
    OPENING_DRIVE_WATCH_MIN,
    evaluate_opening_drive,
    opening_drive_to_dict,
    opening_drive_window_active,
)

ET = ZoneInfo("America/New_York")


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_bars(conn: sqlite3.Connection, ticker: str):
    rows = []
    for i in range(25):
        close = 100 + i * 0.3
        rows.append(
            {
                "ticker": ticker,
                "date": f"2026-01-{i + 1:02d}",
                "open": close * 0.99,
                "high": close * 1.02,
                "low": close * 0.98,
                "close": close,
                "volume": 5_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def test_opening_drive_window_active():
    active = datetime(2026, 8, 4, 9, 40, tzinfo=ET)
    inactive = datetime(2026, 8, 4, 10, 5, tzinfo=ET)
    weekend = datetime(2026, 8, 2, 9, 40, tzinfo=ET)
    assert opening_drive_window_active(active) is True
    assert opening_drive_window_active(inactive) is False
    assert opening_drive_window_active(weekend) is False


def test_opening_drive_pass_strong_open():
    conn = _conn()
    try:
        _seed_bars(conn, "AAPL")
        when = datetime(2026, 8, 4, 9, 40, tzinfo=ET)
        quote = {
            "price": 101.2,
            "open": 100.5,
            "high": 101.5,
            "low": 100.4,
            "prev_close": 99.8,
        }
        spy_quote = {
            "price": 400.5,
            "open": 400.0,
            "high": 401.0,
            "low": 399.8,
            "prev_close": 399.5,
        }
        market_activity = {"allow_trade": True, "band": "above_average", "score": 75}
        with patch(
            "investment_agent.opening_drive.assess_entry_tradability",
            return_value={"verdict": "TRADABLE", "checks": []},
        ):
            result = evaluate_opening_drive(
                conn,
                "AAPL",
                quote=quote,
                spy_quote=spy_quote,
                market_activity=market_activity,
                deploy_dollar=10_000,
                net_target=150,
                when=when,
            )
        assert result["active"] is True
        assert result["score"] >= OPENING_DRIVE_PASS_MIN
        assert result["verdict"] == "pass"
        assert result["eligible_early_entry"] is True
        out = opening_drive_to_dict(result)
        assert out["verdict_label"] == "OPEN DRIVE PASS"
    finally:
        conn.close()


def test_opening_drive_blocked_on_no_trade_day():
    conn = _conn()
    try:
        when = datetime(2026, 8, 4, 9, 40, tzinfo=ET)
        quote = {"price": 101.0, "open": 100.0, "high": 101.5, "low": 99.9, "prev_close": 99.5}
        result = evaluate_opening_drive(
            conn,
            "AAPL",
            quote=quote,
            spy_quote=quote,
            market_activity={"allow_trade": False, "score": 50},
            deploy_dollar=10_000,
            net_target=150,
            when=when,
        )
        assert result["verdict"] == "blocked"
        assert result["eligible_early_entry"] is False
    finally:
        conn.close()


def test_opening_drive_inactive_outside_window():
    conn = _conn()
    try:
        when = datetime(2026, 8, 4, 10, 15, tzinfo=ET)
        quote = {"price": 101.0, "open": 100.0, "high": 101.5, "low": 99.9, "prev_close": 99.5}
        result = evaluate_opening_drive(
            conn,
            "AAPL",
            quote=quote,
            spy_quote=quote,
            market_activity={"allow_trade": True, "score": 75},
            deploy_dollar=10_000,
            net_target=150,
            when=when,
        )
        assert result["verdict"] == "inactive"
        assert result["eligible_early_entry"] is False
    finally:
        conn.close()


def test_opening_drive_watch_band():
    conn = _conn()
    try:
        when = datetime(2026, 8, 4, 9, 40, tzinfo=ET)
        # Flat vs open, modest gap — likely mid score
        quote = {
            "price": 100.05,
            "open": 100.0,
            "high": 100.2,
            "low": 99.95,
            "prev_close": 99.9,
        }
        market_activity = {"allow_trade": True, "score": 72}
        with patch(
            "investment_agent.opening_drive.assess_entry_tradability",
            return_value={"verdict": "CAUTION", "checks": []},
        ):
            result = evaluate_opening_drive(
                conn,
                "AAPL",
                quote=quote,
                spy_quote=quote,
                market_activity=market_activity,
                deploy_dollar=10_000,
                net_target=150,
                when=when,
            )
        assert OPENING_DRIVE_WATCH_MIN <= result["score"] < OPENING_DRIVE_PASS_MIN or result["verdict"] in (
            "watch",
            "fade",
        )
        assert result["eligible_early_entry"] is False
    finally:
        conn.close()
