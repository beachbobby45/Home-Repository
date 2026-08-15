"""Tests for Exceptional trade override (Phase 1B Inc 17)."""

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

from investment_agent.db import init_db, insert_regime_snapshot
from investment_agent.exceptional_trade import (
    MAX_EXCEPTIONAL_TRADES_PER_WEEK,
    count_exceptional_trades_consumed,
    evaluate_exceptional_trade,
    log_exceptional_trade_consumed,
)
from investment_agent.journal import insert_trade
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


def _ma(*, band: str = "exceptional", allow_trade: bool = True) -> dict:
    return {"band": band, "allow_trade": allow_trade, "score": 92, "summary": "Exceptional day"}


def _confirmations(*, ticker: str = "AAPL", passes: bool = True, score: int = 88) -> list[dict]:
    return [{"ticker": ticker, "passes": passes, "score": score}]


def test_evaluate_inactive_when_weekly_not_met():
    result = evaluate_exceptional_trade(
        weekly_target_met=False,
        market_activity=_ma(),
        confirmations=_confirmations(),
        pick_ticker="AAPL",
        phase="trade_window",
        stopped=False,
        open_positions_count=0,
        portfolio_risk_verdict="approved",
        exceptional_consumed_this_week=0,
    )
    assert result["active"] is False
    assert "not yet met" in (result["summary"] or "").lower()


def test_evaluate_active_when_all_signals_go():
    result = evaluate_exceptional_trade(
        weekly_target_met=True,
        market_activity=_ma(),
        confirmations=_confirmations(),
        pick_ticker="AAPL",
        phase="trade_window",
        stopped=False,
        open_positions_count=0,
        portfolio_risk_verdict="approved",
        exceptional_consumed_this_week=0,
    )
    assert result["active"] is True
    assert result["eligible"] is True
    assert result["slot_available"] is True
    assert all(c["ok"] for c in result["checks"])


def test_evaluate_slot_unavailable_after_consumed():
    result = evaluate_exceptional_trade(
        weekly_target_met=True,
        market_activity=_ma(),
        confirmations=_confirmations(),
        pick_ticker="AAPL",
        phase="trade_window",
        stopped=False,
        open_positions_count=0,
        portfolio_risk_verdict="approved",
        exceptional_consumed_this_week=MAX_EXCEPTIONAL_TRADES_PER_WEEK,
    )
    assert result["active"] is False
    assert result["slot_available"] is False
    assert "already used" in (result["summary"] or "").lower()


def test_log_exceptional_trade_consumed():
    conn = _conn()
    try:
        with patch("investment_agent.exceptional_trade.today_pt_str", return_value="2026-08-04"):
            log_exceptional_trade_consumed(
                conn,
                session_date_et="2026-08-04",
                ticker="AAPL",
                journal_buy_id=42,
                market_activity=_ma(),
                confirmation_score=88,
            )
            conn.commit()
            assert count_exceptional_trades_consumed(conn, date_key="2026-08-04") == 1
    finally:
        conn.close()


def test_build_trading_day_status_includes_exceptional_trade():
    conn = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": 0.5,
                "dia_change_pct": 0.4,
                "qqq_change_pct": 0.6,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK",
            },
        )
        conn.commit()
        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert "exceptional_trade" in status
        assert "exceptional_trade" in status["phase1b"]
        assert "show_exceptional_banner" in status["phase1b"]
    finally:
        conn.close()


def test_journal_buy_logs_exceptional_when_active():
    conn = _conn()
    try:
        trade_id = insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            executed_at="2026-08-03T17:30:00+00:00",
        )
        log_exceptional_trade_consumed(
            conn,
            session_date_et="2026-08-03",
            ticker="AAPL",
            journal_buy_id=trade_id,
            market_activity=_ma(),
            confirmation_score=90,
            notes="Exceptional override consumed on journal BUY",
        )
        conn.commit()
        assert count_exceptional_trades_consumed(conn) == 1
    finally:
        conn.close()
