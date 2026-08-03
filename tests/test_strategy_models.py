"""Tests for strategy models and daily profit targets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import daily_profit_target, growth_plan_milestones, next_growth_tier
from investment_agent.strategy_models import target_pct_for_dollars


def test_daily_profit_target_scales_every_5k():
    assert daily_profit_target(10_000) == 150
    assert daily_profit_target(14_999) == 150
    assert daily_profit_target(15_000) == 200
    assert daily_profit_target(20_000) == 250
    assert daily_profit_target(25_000) == 300


def test_growth_plan_milestones():
    rows = growth_plan_milestones(max_balance=25_000)
    assert rows[0] == {"balance_at_least": 10_000.0, "daily_target": 150.0}
    assert rows[2] == {"balance_at_least": 20_000.0, "daily_target": 250.0}


def test_next_growth_tier():
    tier = next_growth_tier(12_500)
    assert tier["current_daily_target"] == 150
    assert tier["next_balance"] == 15_000
    assert tier["next_daily_target"] == 200
    assert tier["amount_to_next_tier"] == 2_500


def test_target_pct_for_dollars_on_10k():
    # need $150 net + $14 fees on ~$10k deploy ≈ 1.64%
    pct = target_pct_for_dollars(net_needed=150, deploy_dollar=10_000, fees=14)
    assert pct is not None
    assert 1.6 < pct < 1.7
