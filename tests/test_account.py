"""Tests for account summary and sweeps."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import (
    apply_month_end_sweep,
    build_dashboard_summary,
    format_journal_notes,
    get_trading_mode,
    set_trading_mode,
    set_setting,
)
from investment_agent.db import init_db, insert_regime_snapshot
from investment_agent.journal import insert_trade


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def test_apply_sweep_on_gain_month():
    conn, path = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T10:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=110,
            fee=7,
            executed_at="2026-07-31T11:00:00+00:00",
        )
        conn.commit()
        result = apply_month_end_sweep(conn, "2026-07")
        assert result["ok"] is True
        assert result["total_sweep"] > 0
        conn.commit()
        summary = build_dashboard_summary(conn)
        assert summary.management_jar > 0
        assert summary.tax_jar > 0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_dashboard_summary_regime_and_tax_rate():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-07-31T12:00:00+00:00",
                "spy_change_pct": -0.5,
                "dia_change_pct": -0.3,
                "qqq_change_pct": -0.1,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        set_setting(conn, "tax_reserve_rate", "0.30")
        conn.commit()
        summary = build_dashboard_summary(conn)
        assert summary.block_new_longs is True
        assert summary.tax_rate == 0.30
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_trading_mode_defaults_to_paper():
    conn, path = _conn()
    try:
        assert get_trading_mode(conn) == "paper"
        summary = build_dashboard_summary(conn)
        assert summary.trading_mode == "paper"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_set_trading_mode_and_journal_note_tagging():
    conn, path = _conn()
    try:
        assert set_trading_mode(conn, "live") == "live"
        assert format_journal_notes("E*TRADE fill", "live") == "[LIVE] E*TRADE fill"
        assert format_journal_notes("[PAPER] already tagged", "live") == "[PAPER] already tagged"
        assert format_journal_notes(None, "paper") == "[PAPER]"
    finally:
        conn.close()
        path.unlink(missing_ok=True)
