"""Tests for trade plan and planned trade validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.trading_day import compute_trade_plan


def test_compute_trade_plan_at_10k():
    plan = compute_trade_plan(entry_price=100.0, deploy_dollar=10_000)
    assert plan["shares"] == 99
    assert plan["target_price"] == 101.5
    assert plan["stop_price"] == 99.25
    assert plan["net_at_target"] > 130
    assert plan["net_at_stop"] < -80


def test_compute_trade_plan_updates_with_price():
    low = compute_trade_plan(entry_price=50.0, deploy_dollar=10_000)
    high = compute_trade_plan(entry_price=55.0, deploy_dollar=10_000)
    assert high["target_price"] > low["target_price"]
    assert high["shares"] < low["shares"]
