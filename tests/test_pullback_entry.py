"""Tests for pullback limit entry planning."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.pullback_entry import (
    compute_pullback_trade_plan,
    limit_buy_price,
    limit_fill_missed,
    simulate_pullback_dollar_outcome,
)
from datetime import time


def test_limit_buy_below_open():
    px = limit_buy_price(100.0, avg_range_pct=3.0)
    assert px < 100.0
    assert px == 98.95  # 100 * (1 - 1.05/100) with 35% of 3% = 1.05%


def test_pullback_plan_needs_smaller_upside_move():
    from investment_agent.trading_day import compute_trade_plan

    session_open = 100.0
    plan = compute_pullback_trade_plan(
        session_open=session_open,
        avg_range_pct=3.0,
        deploy_dollar=10_000,
        net_target=150.0,
    )
    at_open = compute_trade_plan(entry_price=session_open, deploy_dollar=10_000, net_target=150.0)
    move_from_open_pct = ((plan["limit_sell_price"] - session_open) / session_open) * 100
    assert plan["limit_buy_price"] < session_open
    assert plan["limit_sell_price"] < at_open["target_price"]
    assert move_from_open_pct < at_open["target_pct"]
    assert plan["estimated_net_at_typical_high"] > at_open["net_at_target"]
    assert plan["net_at_target"] >= 149.0


def test_simulate_pullback_no_fill_when_low_stays_above_limit():
    outcome = simulate_pullback_dollar_outcome(
        100.0,
        high=101.0,
        low=99.5,
        deploy_dollar=10_000,
        avg_range_pct=3.0,
        net_target=150.0,
    )
    assert outcome == "no_fill"


def test_simulate_pullback_target_when_dip_then_rally():
    limit = limit_buy_price(100.0, 3.0)
    outcome = simulate_pullback_dollar_outcome(
        100.0,
        high=100.0 + (100.0 - limit) + 2.0,
        low=limit - 0.01,
        deploy_dollar=10_000,
        avg_range_pct=3.0,
        net_target=150.0,
    )
    assert outcome == "target"


def test_limit_fill_missed_after_deadline():
    limit = limit_buy_price(100.0, 3.0)
    assert limit_fill_missed(
        limit_buy_price=limit,
        session_low=limit + 0.05,
        as_of_time=time(12, 0),
    )
    assert not limit_fill_missed(
        limit_buy_price=limit,
        session_low=limit - 0.01,
        as_of_time=time(12, 0),
    )
