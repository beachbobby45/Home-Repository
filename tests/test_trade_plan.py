"""Tests for trade plan and planned trade validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import sell_price_for_net_target
from investment_agent.trading_day import compute_trade_plan


def test_compute_trade_plan_growth_plan_150_net_at_10k():
    plan = compute_trade_plan(entry_price=100.0, deploy_dollar=10_000, net_target=150)
    assert plan["shares"] == 99
    assert plan["stop_price"] == 99.25
    assert plan["net_target"] == 150
    assert plan["net_at_target"] >= 149
    assert plan["net_at_target"] <= 151
    assert plan["target_pct"] > 1.6
    assert plan["net_at_stop"] < -80


def test_compute_trade_plan_scales_down_pct_at_15k():
    plan_10 = compute_trade_plan(entry_price=100.0, deploy_dollar=10_000, net_target=150)
    plan_15 = compute_trade_plan(entry_price=100.0, deploy_dollar=15_000, net_target=200)
    assert plan_15["target_pct"] < plan_10["target_pct"]
    assert plan_15["net_target"] == 200


def test_compute_trade_plan_updates_with_price():
    low = compute_trade_plan(entry_price=50.0, deploy_dollar=10_000, net_target=150)
    high = compute_trade_plan(entry_price=55.0, deploy_dollar=10_000, net_target=150)
    assert high["target_price"] > low["target_price"]
    assert high["shares"] < low["shares"]


def test_sell_price_for_net_target():
    px = sell_price_for_net_target(entry_price=72.79, shares=137, net_target=150)
    net = 137 * (px - 72.79) - 14
    assert abs(net - 150) < 0.05
