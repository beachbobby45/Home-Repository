"""Tests for 10-year growth plan table API."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.dashboard.app import app
from investment_agent.db import init_db
from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE, GOAL_ACCOUNT_VALUE
from investment_agent.growth_projection import (
    PAPER_HISTORY_START,
    PAPER_HISTORY_YEAR,
    PLAN_FUNDED_TARGET,
    PLAN_START_CALENDAR_YEAR,
    PLAN_STARTING_BASIS,
    RH_LIVE_DATE,
    build_ten_year_growth_plan,
)


def test_build_ten_year_has_paper_then_live_rows():
    data = build_ten_year_growth_plan()
    assert data["years"][0]["year"] == PAPER_HISTORY_YEAR == 2026
    assert data["years"][0]["is_paper_history"] is True
    assert data["years"][1]["year"] == PLAN_START_CALENDAR_YEAR == 2027
    assert data["years"][1]["is_paper_history"] is False
    assert data["years"][-1]["year"] == 2038
    assert data["calendar_year_start"] == 2026
    assert data["live_start_year"] == 2027
    assert len(data["years"]) == 13  # 2026 paper + 12 live years


def test_2027_begin_is_exactly_15k_not_paper_remaining():
    data = build_ten_year_growth_plan()
    y2026 = data["years"][0]
    y2027 = data["years"][1]
    assert y2026["injection"]["start_balance"] == PAPER_HISTORY_START
    # Without ledger fills, paper remaining == begin
    assert y2026["injection"]["end_balance"] == PAPER_HISTORY_START
    assert y2027["injection"]["start_balance"] == PLAN_STARTING_BASIS == 15_000.0
    assert y2027["injection"]["capital_injection"] == 15_000.0
    # Critical: 2027 Begin is NOT 2026 Remaining (even when they happen to match at $5k stub)
    assert y2027["injection"]["start_balance"] == 15_000.0
    assert y2027["injection"]["start_balance"] != y2026["injection"]["end_balance"] or (
        y2026["injection"]["end_balance"] == 5_000.0
    )


def test_paper_row_uses_gate_trading_pnl():
    tmp = tempfile.TemporaryDirectory()
    db = Path(tmp.name) / "t.db"
    init_db(db)
    import sqlite3

    from investment_agent.execution.paper_ledger import (
        ACCOUNT_GATE,
        apply_round_trip,
        ensure_paper_accounts,
        upsert_session_log,
    )

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    ensure_paper_accounts(conn, starting_cash=5_000.0)
    rt = apply_round_trip(
        conn,
        account_name=ACCOUNT_GATE,
        session_date_et="2026-10-21",
        ticker="TEST",
        shares=10,
        entry_price=100.0,
        exit_price=101.5,
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
        fill_ts="2026-10-21T10:00:00-04:00",
        exit_ts="2026-10-21T11:00:00-04:00",
    )
    upsert_session_log(
        conn,
        {
            "session_date_et": "2026-10-21",
            "account_name": ACCOUNT_GATE,
            "ticker": "TEST",
            "status": "complete",
            "filled": True,
            "fill_ts": "2026-10-21T10:00:00-04:00",
            "exit_ts": "2026-10-21T11:00:00-04:00",
            "entry_price": 100.0,
            "exit_price": 101.5,
            "shares": 10,
            "deploy": 1000.0,
            "net_pnl": rt["net_pnl"],
            "settled_cash_before": rt["settled_before"],
            "settled_cash_after": rt["settled_after"],
            "equity_after": rt["equity_after"],
        },
    )
    conn.commit()
    data = build_ten_year_growth_plan(conn=conn)
    y2026 = data["years"][0]
    y2027 = data["years"][1]
    assert y2026["injection"]["gross_production"] == 15.0  # 10 * 1.5
    assert y2026["injection"]["end_balance"] == 5_015.0
    assert y2027["injection"]["start_balance"] == 15_000.0
    assert "does not transfer" in y2026["injection"]["notes"]
    conn.close()
    tmp.cleanup()


def test_months_to_goal_present():
    data = build_ten_year_growth_plan()
    base_m = data["months_to_goal"]["base"]
    inj_m = data["months_to_goal"]["injection"]
    assert base_m is not None and inj_m is not None
    assert inj_m == base_m


def test_plan_starts_live_at_fifteen_k():
    data = build_ten_year_growth_plan()
    assert data["starting_basis"] == PLAN_STARTING_BASIS == 15_000.0
    assert data["funded_target"] == PLAN_FUNDED_TARGET
    assert data["assumptions"]["paper_does_not_transfer"] is True
    assert data["assumptions"]["rh_live_date"] == RH_LIVE_DATE == "2027-01-04"
    assert "does not transfer" in data["summary"]


def test_api_growth_plan_ten_year():
    client = TestClient(app)
    resp = client.get("/api/growth-plan/ten-year")
    assert resp.status_code == 200
    data = resp.json()
    assert data["starting_basis"] == PLAN_STARTING_BASIS
    assert data["goal"] == GOAL_ACCOUNT_VALUE
    assert data["years"][0]["year"] == 2026
    assert data["years"][1]["year"] == 2027
    assert data["years"][1]["injection"]["start_balance"] == 15_000.0
