"""Tests for Phase 1 Risk Engine (Increment 1)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import set_setting
from investment_agent.db import init_db
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import count_buys_today, compute_weekly_realized_net, insert_trade
from investment_agent.risk_engine import (
    KILL_SWITCH_KEY,
    PHASE1_HIGH_WATER_KEY,
    MarketSnapshot,
    PortfolioSnapshot,
    RiskConfig,
    TradeProposalPlan,
    auto_engaged_kill_switch,
    build_portfolio_snapshot,
    evaluate_proposal,
    is_kill_switch_active,
    portfolio_allows_new_entries,
    portfolio_status_dict,
    set_kill_switch,
)
from fastapi.testclient import TestClient
from unittest.mock import patch

from investment_agent.dashboard.app import app

PT = ZoneInfo("America/Los_Angeles")
TODAY = "2026-08-14T14:00:00-07:00"


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _good_proposal(**overrides) -> TradeProposalPlan:
    defaults = dict(
        ticker="NFLX",
        entry_price=100.0,
        stop_price=99.25,
        target_price=102.0,
        shares=100,
        liquidity_cap=10_000.0,
    )
    defaults.update(overrides)
    return TradeProposalPlan(**defaults)


def _healthy_portfolio(**overrides) -> PortfolioSnapshot:
    defaults = dict(
        tradable_cash=10_000.0,
        open_positions=[],
        today_realized_net=0.0,
        weekly_realized_net=0.0,
        buys_today=0,
        high_water_mark=10_000.0,
        current_equity=10_000.0,
        drawdown_pct=0.0,
        kill_switch_active=False,
    )
    defaults.update(overrides)
    return PortfolioSnapshot(**defaults)


def _healthy_market() -> MarketSnapshot:
    return MarketSnapshot(block_new_longs=False, regime_summary="Regime OK")


def test_kill_switch_blocks_proposal():
    portfolio = _healthy_portfolio(kill_switch_active=True)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("Kill switch" in b for b in decision.blockers)


def test_daily_loss_limit_rejects():
    portfolio = _healthy_portfolio(today_realized_net=-201.0)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("Daily loss" in b for b in decision.blockers)


def test_weekly_loss_limit_rejects():
    portfolio = _healthy_portfolio(weekly_realized_net=-501.0)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("Weekly loss" in b for b in decision.blockers)


def test_max_open_positions_rejects():
    positions = [
        {"ticker": "AAPL", "shares": 10, "avg_cost": 100, "cost_basis": 1007},
        {"ticker": "MSFT", "shares": 5, "avg_cost": 200, "cost_basis": 1007},
    ]
    portfolio = _healthy_portfolio(open_positions=positions)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("open position" in b.lower() for b in decision.blockers)


def test_max_trades_per_day_rejects():
    portfolio = _healthy_portfolio(buys_today=2)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("trades" in b.lower() for b in decision.blockers)


def test_drawdown_halt_rejects():
    portfolio = _healthy_portfolio(
        high_water_mark=11_000.0,
        current_equity=9_800.0,
        drawdown_pct=10.91,
    )
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("drawdown" in b.lower() for b in decision.blockers)


def test_regime_blocks_new_longs():
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=_healthy_portfolio(),
        market=MarketSnapshot(block_new_longs=True, regime_summary="All indices down"),
    )
    assert decision.verdict == "rejected"
    assert any("Regime" in b for b in decision.blockers)


def test_mandatory_stop_invalid_rejects():
    decision = evaluate_proposal(
        proposal=_good_proposal(stop_price=100.5),
        portfolio=_healthy_portfolio(),
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("stop" in b.lower() for b in decision.blockers)


def test_max_risk_per_trade_rejects_oversized():
    decision = evaluate_proposal(
        proposal=_good_proposal(shares=500),
        portfolio=_healthy_portfolio(),
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("risk" in b.lower() for b in decision.blockers)


def test_min_reward_risk_rejects():
    decision = evaluate_proposal(
        proposal=_good_proposal(target_price=100.5),
        portfolio=_healthy_portfolio(),
        market=_healthy_market(),
    )
    assert decision.verdict == "rejected"
    assert any("Reward:risk" in b or "R:R" in b for b in decision.blockers)


def test_approved_proposal_within_limits():
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=_healthy_portfolio(),
        market=_healthy_market(),
    )
    assert decision.verdict == "approved"
    assert decision.max_risk_dollars == 100.0
    assert decision.recommended_shares >= 99


def test_portfolio_allows_new_entries_when_flat():
    conn, path = _conn()
    try:
        decision = portfolio_allows_new_entries(conn)
        assert decision.verdict == "approved"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_portfolio_snapshot_tracks_high_water():
    conn, path = _conn()
    try:
        set_setting(conn, PHASE1_HIGH_WATER_KEY, "10500")
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at=TODAY,
        )
        conn.commit()
        snap = build_portfolio_snapshot(conn, date_key="2026-08-14")
        assert snap.high_water_mark == 10_500.0
        assert snap.tradable_cash < ORIGINAL_BASIS
        assert len(snap.open_positions) == 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_auto_engaged_kill_switch_on_drawdown():
    conn, path = _conn()
    try:
        set_setting(conn, PHASE1_HIGH_WATER_KEY, "11000")
        snap = PortfolioSnapshot(
            tradable_cash=9_000.0,
            open_positions=[],
            today_realized_net=0.0,
            weekly_realized_net=0.0,
            buys_today=0,
            high_water_mark=11_000.0,
            current_equity=9_000.0,
            drawdown_pct=18.18,
            kill_switch_active=False,
        )
        assert auto_engaged_kill_switch(conn, snap) is True
        assert is_kill_switch_active(conn)
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_count_buys_today_from_journal():
    conn, path = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            executed_at=TODAY,
        )
        insert_trade(
            conn,
            ticker="MSFT",
            side="BUY",
            shares=5,
            price=200,
            executed_at="2026-08-13T14:00:00-07:00",
        )
        conn.commit()
        assert count_buys_today(conn, "2026-08-14") == 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_weekly_realized_net_monday_through_friday():
    conn, path = _conn()
    try:
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100,
            fee=7,
            executed_at="2026-08-11T10:00:00-07:00",
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=90,
            fee=7,
            executed_at="2026-08-12T15:00:00-07:00",
        )
        conn.commit()
        weekly = compute_weekly_realized_net(conn, "2026-08-14")
        assert weekly < -100
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_portfolio_status_dict_includes_limits():
    snap = _healthy_portfolio()
    status = portfolio_status_dict(snap)
    assert status["limits"]["max_open_positions"] == 2
    assert status["daily_loss_limit_dollars"] == 200.0
    assert status["weekly_loss_limit_dollars"] == 500.0


def test_set_kill_switch_persists():
    conn, path = _conn()
    try:
        set_kill_switch(conn, True)
        conn.commit()
        assert is_kill_switch_active(conn)
        set_kill_switch(conn, False)
        assert not is_kill_switch_active(conn)
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_api_risk_status():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/api/risk/status")
                assert resp.status_code == 200
                data = resp.json()
                assert data["tradable_cash"] == 10_000.0
                assert data["limits"]["max_trades_per_day"] == 2


def test_api_kill_switch_toggle():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.post("/api/risk/kill-switch", json={"active": True})
                assert resp.status_code == 200
                assert resp.json()["kill_switch_active"] is True
                resp2 = client.post("/api/risk/kill-switch", json={"active": False})
                assert resp2.json()["kill_switch_active"] is False


def test_daily_loss_at_boundary_allows():
    portfolio = _healthy_portfolio(today_realized_net=-199.0)
    decision = evaluate_proposal(
        proposal=_good_proposal(),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "approved"


def test_one_open_position_allows_second():
    positions = [{"ticker": "AAPL", "shares": 10, "avg_cost": 100, "cost_basis": 1007}]
    portfolio = _healthy_portfolio(open_positions=positions)
    decision = evaluate_proposal(
        proposal=_good_proposal(shares=50),
        portfolio=portfolio,
        market=_healthy_market(),
    )
    assert decision.verdict == "approved"
