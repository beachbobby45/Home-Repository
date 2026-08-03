"""Tests for trade journal and P&L."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import (
    build_executed_at_et,
    clear_all_trades,
    compute_monthly_realized_net,
    insert_trade,
    journal_cash_balance,
    list_trades,
    resolve_executed_at,
)


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    return sqlite3.connect(path), path


def test_journal_cash_balance_after_round_trip():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T14:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7,
            executed_at="2026-07-31T15:00:00+00:00",
        )
        conn.commit()
        cash = journal_cash_balance(conn)
        # Buy 1007, sell proceeds 1004.3 → net cash −2.7 vs basis
        assert abs(cash - (ORIGINAL_BASIS - 2.7)) < 0.01
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_monthly_realized_net_includes_fees():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-07-31T14:00:00+00:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7,
            executed_at="2026-07-31T15:00:00+00:00",
        )
        conn.commit()
        net = compute_monthly_realized_net(conn, "2026-07")
        # Gross +11.3, fees 14 → net −2.7
        assert abs(net - (-2.7)) < 0.01
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_clear_all_trades_resets_cash_to_basis():
    conn, path = _conn()
    try:
        conn.row_factory = sqlite3.Row
        insert_trade(conn, ticker="AAPL", side="BUY", shares=10, price=100, fee=7)
        insert_trade(conn, ticker="AAPL", side="SELL", shares=10, price=110, fee=7)
        conn.commit()
        assert journal_cash_balance(conn) != ORIGINAL_BASIS
        removed = clear_all_trades(conn)
        conn.commit()
        assert removed == 2
        assert list_trades(conn) == []
        assert journal_cash_balance(conn) == ORIGINAL_BASIS
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_executed_at_et_combines_date_and_time():
    iso = build_executed_at_et("2026-08-03", "10:15")
    assert iso.startswith("2026-08-03T10:15:00")
    assert "-04:00" in iso or "-05:00" in iso


def test_resolve_executed_at_prefers_audit_fields():
    resolved = resolve_executed_at(
        executed_date="2026-08-03",
        executed_time_et="14:30",
    )
    assert resolved is not None
    assert "2026-08-03T14:30:00" in resolved
