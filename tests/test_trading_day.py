"""Tests for intraday trading day go/no-go panel."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.trading_day import build_trading_day_status, session_phase, stopped_out_today

ET = ZoneInfo("America/New_York")


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _metric(conn, ticker: str):
    insert_ticker_metrics(
        conn,
        {
            "ticker": ticker,
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


def test_session_phase_opening_wait():
    dt = datetime(2026, 8, 3, 9, 45, tzinfo=ET)
    assert session_phase(dt) == "opening_wait"


def test_session_phase_trade_window():
    dt = datetime(2026, 8, 3, 11, 0, tzinfo=ET)
    assert session_phase(dt) == "trade_window"


def test_trading_day_status_wait_during_opening():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": 0.2,
                "dia_change_pct": 0.1,
                "qqq_change_pct": 0.3,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 9, 50, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "WAIT"
        assert status["session_phase"] == "opening_wait"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_trading_day_no_go_when_regime_blocks():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": -0.5,
                "dia_change_pct": -0.3,
                "qqq_change_pct": -0.1,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "NO_GO"
        assert status["can_enter_new"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)
