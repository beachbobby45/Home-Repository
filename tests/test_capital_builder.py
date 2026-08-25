"""Tests for Phase 1 Capital Builder progress (Increment 5 + Phase 1B tier model)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.account import set_setting
from investment_agent.capital_builder import (
    PHASE1_START,
    PHASE1_TARGET,
    SOFT_TARGET_NOTE,
    build_capital_builder_progress,
    phase1_journey_progress_pct,
    phase1_of_target_pct,
    progress_to_dict,
    weekly_production_progress_pct,
)
from investment_agent.dashboard.app import app
from investment_agent.db import init_db
from investment_agent.finance import weekly_production_target
from investment_agent.journal import compute_weekly_realized_net, insert_trade, journal_cash_balance
from investment_agent.risk_engine import PHASE1_HIGH_WATER_KEY

MONDAY = "2026-08-10T10:00:00-07:00"
FRIDAY = "2026-08-14T14:00:00-07:00"


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _set_tradable_cash(conn: sqlite3.Connection, target: float) -> None:
    """Adjust journal cash to ``target`` via a closed round trip."""
    current = journal_cash_balance(conn)
    delta = round(target - current, 2)
    if abs(delta) < 0.01:
        return
    buy_price = 100.0
    buy_fee = 7.0
    sell_fee = 7.0
    shares = max(10, int(abs(delta) / 25) + 1)
    insert_trade(
        conn,
        ticker="NFLX",
        side="BUY",
        shares=shares,
        price=buy_price,
        fee=buy_fee,
        executed_at=MONDAY,
        notes="seed buy",
    )
    sell_price = buy_price + (delta + buy_fee + sell_fee) / shares
    assert sell_price > 0, f"cannot seed cash delta {delta} with {shares} shares"
    insert_trade(
        conn,
        ticker="NFLX",
        side="SELL",
        shares=shares,
        price=sell_price,
        fee=sell_fee,
        executed_at=FRIDAY,
        notes="seed sell",
    )
    conn.commit()


def test_phase1_journey_progress_at_start():
    assert phase1_journey_progress_pct(PHASE1_START) == 0.0


def test_phase1_journey_progress_midpoint():
    mid = PHASE1_START + (PHASE1_TARGET - PHASE1_START) / 2
    assert phase1_journey_progress_pct(mid) == 50.0


def test_phase1_journey_progress_at_target():
    assert phase1_journey_progress_pct(PHASE1_TARGET) == 100.0


def test_phase1_journey_progress_clamped_below_start():
    assert phase1_journey_progress_pct(PHASE1_START - 500) == 0.0


def test_phase1_of_target_pct():
    assert phase1_of_target_pct(12_450) == (12_450 / PHASE1_TARGET) * 100


def test_weekly_production_progress_at_10k_tier():
    assert abs(weekly_production_progress_pct(150, 450) - (100 / 3)) < 0.01
    assert weekly_production_progress_pct(450, 450) == 100.0


def test_build_progress_includes_tier_at_10k():
    conn, path = _conn()
    try:
        _set_tradable_cash(conn, 10_000)
        conn.commit()
        progress = build_capital_builder_progress(conn)
        assert progress.daily_production_target == 150.0
        assert progress.weekly_production_target == 450.0
        assert progress.structure_label == "$10K"
        assert progress.weekly_opportunities == 3
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_progress_includes_high_water_and_drawdown():
    conn, path = _conn()
    try:
        _set_tradable_cash(conn, 12_800)
        set_setting(conn, PHASE1_HIGH_WATER_KEY, "12800")
        conn.commit()

        with patch(
            "investment_agent.capital_builder.today_pt_str",
            return_value=FRIDAY.split("T")[0],
        ):
            progress = build_capital_builder_progress(conn, date_key=FRIDAY.split("T")[0])

        assert progress.current_equity == 12_800.0
        assert progress.tier_threshold == 10_000.0
        assert progress.daily_production_target == 150.0
        assert progress.high_water_mark == 12_800.0
        assert progress.drawdown_pct == 0.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_progress_reflects_drawdown():
    conn, path = _conn()
    try:
        _set_tradable_cash(conn, 12_450)
        set_setting(conn, PHASE1_HIGH_WATER_KEY, "12800")
        conn.commit()

        progress = build_capital_builder_progress(conn)
        assert progress.high_water_mark == 12_800.0
        assert progress.drawdown_pct > 0
        assert progress.current_equity == 12_450.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_progress_weekly_realized_net():
    conn, path = _conn()
    try:
        _set_tradable_cash(conn, 10_000)
        insert_trade(
            conn,
            ticker="NFLX",
            side="BUY",
            shares=10,
            price=100.0,
            fee=7.0,
            executed_at=MONDAY,
            notes="buy",
        )
        insert_trade(
            conn,
            ticker="NFLX",
            side="SELL",
            shares=10,
            price=132.0,
            fee=7.0,
            executed_at=FRIDAY,
            notes="sell",
        )
        conn.commit()

        with patch(
            "investment_agent.capital_builder.today_pt_str",
            return_value=FRIDAY.split("T")[0],
        ):
            progress = build_capital_builder_progress(conn, date_key=FRIDAY.split("T")[0])

        expected_weekly = compute_weekly_realized_net(conn, FRIDAY.split("T")[0])
        assert progress.weekly_realized_net == expected_weekly
        assert progress.weekly_production_target == 450.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_progress_to_dict_includes_tier_fields():
    conn, path = _conn()
    try:
        _set_tradable_cash(conn, 10_000)
        conn.commit()
        payload = progress_to_dict(build_capital_builder_progress(conn))
        assert payload["phase1_start"] == PHASE1_START
        assert payload["weekly_production_target"] == 450.0
        assert payload["daily_production_target"] == 150.0
        assert payload["structure_label"] == "$10K"
        assert payload["weekly_soft_target"] == 450.0
        assert payload["soft_target_note"] == SOFT_TARGET_NOTE
        assert payload["milestone_reached"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_api_capital_builder_progress():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            _set_tradable_cash(conn, 12_450)
        finally:
            conn.close()

        def fake_connect():
            c = sqlite3.connect(db_path)
            c.row_factory = sqlite3.Row
            return c

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/api/capital-builder/progress")
                assert resp.status_code == 200
                data = resp.json()
                assert data["current_equity"] == 12_450.0
                assert data["daily_production_target"] == 150.0
                assert data["weekly_production_target"] == weekly_production_target(12_450)
