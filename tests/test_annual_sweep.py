"""Tests for annual sweep schedule."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import (
    apply_annual_sweep,
    apply_period_sweep,
    build_dashboard_summary,
    get_sweep_schedule,
    set_sweep_schedule,
)
from investment_agent.db import init_db
from investment_agent.journal import insert_trade


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def test_default_sweep_schedule_is_annual():
    conn, path = _conn()
    try:
        assert get_sweep_schedule(conn) == "annual"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_apply_annual_sweep_on_ytd_gain():
    conn, path = _conn()
    try:
        set_sweep_schedule(conn, "annual")
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
        result = apply_annual_sweep(conn, "2026")
        assert result["ok"] is True
        assert result["total_sweep"] > 0
        conn.commit()
        summary = build_dashboard_summary(conn)
        assert summary.sweep_schedule == "annual"
        assert summary.period_realized_net > 0
        assert summary.sweep_already_applied is True
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_apply_period_sweep_routes_to_annual():
    conn, path = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-03-01T10:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=110,
            fee=7,
            executed_at="2026-03-01T11:00:00+00:00",
        )
        conn.commit()
        result = apply_period_sweep(conn)
        assert result["ok"] is True
        assert result["sweep_schedule"] == "annual"
    finally:
        conn.close()
        path.unlink(missing_ok=True)
