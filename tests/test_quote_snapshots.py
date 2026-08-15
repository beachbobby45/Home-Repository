"""Tests for scheduled intraday quote snapshots (Phase 1B Inc 11)."""

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

from investment_agent.db import init_db
from investment_agent.quote_snapshots import (
    get_session_snapshot_status,
    get_snapshots_for_tickers,
    maybe_record_snapshots_after_refresh,
    record_snapshots_from_quote_rows,
    snapshot_slot_for_time,
    upsert_quote_snapshot,
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


def test_snapshot_slot_for_time_windows():
    monday = ET
    assert snapshot_slot_for_time(datetime(2026, 8, 3, 8, 0, tzinfo=monday)) == "pre_market"
    assert snapshot_slot_for_time(datetime(2026, 8, 3, 9, 35, tzinfo=monday)) == "at_open"
    assert snapshot_slot_for_time(datetime(2026, 8, 3, 9, 50, tzinfo=monday)) == "plus_15m"
    assert snapshot_slot_for_time(datetime(2026, 8, 3, 11, 0, tzinfo=monday)) is None
    assert snapshot_slot_for_time(datetime(2026, 8, 2, 10, 0, tzinfo=monday)) is None  # Saturday


def test_upsert_and_session_status():
    conn = _conn()
    try:
        upsert_quote_snapshot(
            conn,
            session_date_et="2026-08-03",
            slot="at_open",
            ticker="SPY",
            captured_at="2026-08-03T13:35:00+00:00",
            price=450.25,
            open_px=449.0,
            prev_close=448.5,
        )
        upsert_quote_snapshot(
            conn,
            session_date_et="2026-08-03",
            slot="at_open",
            ticker="AAPL",
            captured_at="2026-08-03T13:35:00+00:00",
            price=210.0,
        )
        conn.commit()

        status = get_session_snapshot_status(conn, "2026-08-03")
        assert status["session_date_et"] == "2026-08-03"
        assert status["complete"] is False
        at_open = next(s for s in status["slots"] if s["slot"] == "at_open")
        assert at_open["captured"] is True
        assert at_open["ticker_count"] == 2
        assert len(at_open["indices"]) == 1
    finally:
        conn.close()


def test_record_snapshots_from_quote_rows():
    conn = _conn()
    try:
        count = record_snapshots_from_quote_rows(
            conn,
            session_date_et="2026-08-03",
            slot="plus_15m",
            quote_rows={
                "QQQ": {"price": 380.0, "captured_at": "2026-08-03T13:50:00+00:00"},
                "BAD": {"price": None},
            },
        )
        assert count == 1
        rows = get_snapshots_for_tickers(conn, ["QQQ"], session_date_et="2026-08-03")
        assert "plus_15m" in rows["QQQ"]
        assert rows["QQQ"]["plus_15m"]["price"] == 380.0
    finally:
        conn.close()


def test_maybe_record_outside_window():
    conn = _conn()
    try:
        when = datetime(2026, 8, 3, 14, 0, tzinfo=ET)
        result = maybe_record_snapshots_after_refresh(
            conn,
            {"SPY": {"price": 450.0, "captured_at": "2026-08-03T18:00:00+00:00"}},
            when=when,
        )
        assert result["recorded"] is False
        assert result["slot"] is None
    finally:
        conn.close()


def test_maybe_record_force_slot():
    conn = _conn()
    try:
        when = datetime(2026, 8, 3, 14, 0, tzinfo=ET)
        result = maybe_record_snapshots_after_refresh(
            conn,
            {
                "SPY": {"price": 451.0, "captured_at": "2026-08-03T18:00:00+00:00"},
                "DIA": {"price": 390.0, "captured_at": "2026-08-03T18:00:00+00:00"},
            },
            when=when,
            force_slot="pre_market",
        )
        assert result["recorded"] is True
        assert result["slot"] == "pre_market"
        assert result["tickers"] == 2
        status = get_session_snapshot_status(conn, "2026-08-03")
        pre = next(s for s in status["slots"] if s["slot"] == "pre_market")
        assert pre["captured"] is True
    finally:
        conn.close()


def test_build_trading_day_status_includes_snapshots():
    from investment_agent.trading_day import build_trading_day_status

    conn = _conn()
    try:
        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 9, 50, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert "quote_snapshots" in status
        assert status["quote_snapshots"]["session_date_et"] == "2026-08-03"
        assert len(status["quote_snapshots"]["slots"]) == 3
    finally:
        conn.close()
