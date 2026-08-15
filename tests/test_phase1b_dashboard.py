"""Tests for Phase 1B dashboard wiring (Inc 14–16)."""

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
from investment_agent.journal import count_weekly_production_opportunities, insert_trade
from investment_agent.trade_proposal import generate_proposals
from investment_agent.trading_day import build_trading_day_status

ET = ZoneInfo("America/New_York")


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def test_count_weekly_production_opportunities():
    conn = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            executed_at="2026-08-04T14:00:00-07:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=115,
            executed_at="2026-08-04T15:00:00-07:00",
        )
        conn.commit()
        with patch("investment_agent.journal.today_pt_str", return_value="2026-08-04"):
            count = count_weekly_production_opportunities(
                conn, date_key="2026-08-04", daily_target=150
            )
        assert count == 1
    finally:
        conn.close()


def test_build_trading_day_status_includes_phase1b():
    conn = _conn()
    try:
        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert "phase1b" in status
        assert "weekly_progress" in status["phase1b"]
        assert "show_no_trade_banner" in status["phase1b"]
        assert "block_new_proposals" in status["phase1b"]
    finally:
        conn.close()


def test_generate_proposals_blocked_on_no_trade_day():
    conn = _conn()
    try:
        with patch("investment_agent.trading_day.session_phase", return_value="trade_window"), patch(
            "investment_agent.market_activity.evaluate_market_activity",
            return_value={"allow_trade": False, "summary": "NO TRADE", "score": 60, "band": "average"},
        ), patch(
            "investment_agent.market_activity.market_activity_to_dict",
            side_effect=lambda x: x,
        ):
            result = generate_proposals(conn)
        assert result["ok"] is False
        assert "DO NOT TRADE" in result["error"]
        assert result["actionable_count"] == 0
    finally:
        conn.close()
