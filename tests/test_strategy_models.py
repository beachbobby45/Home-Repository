"""Tests for strategy models and daily profit targets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import (
    capital_tier_detail,
    daily_profit_target,
    growth_plan_milestones,
    next_growth_tier,
    weekly_production_target,
)
from investment_agent.strategy_models import target_pct_for_dollars


def test_daily_profit_target_split_lot_tiers():
    assert daily_profit_target(10_000) == 150
    assert daily_profit_target(14_999) == 150
    assert daily_profit_target(15_000) == 200
    assert daily_profit_target(20_000) == 300
    assert daily_profit_target(25_000) == 350
    assert daily_profit_target(30_000) == 400


def test_weekly_production_target_three_times_daily():
    assert weekly_production_target(10_000) == 450
    assert weekly_production_target(20_000) == 900
    assert weekly_production_target(30_000) == 1200


def test_capital_tier_detail_structure():
    detail = capital_tier_detail(25_000)
    assert detail["structure_label"] == "$10K + $15K"
    assert detail["daily_production_target"] == 350
    assert detail["weekly_production_target"] == 1050


def test_growth_plan_milestones():
    rows = growth_plan_milestones(max_balance=30_000)
    assert rows[0]["balance_at_least"] == 15_000.0
    assert rows[0]["daily_target"] == 200.0
    assert rows[0]["weekly_target"] == 600.0
    row_20k = next(r for r in rows if r["balance_at_least"] == 20_000.0)
    assert row_20k["daily_target"] == 300.0
    assert row_20k["structure_label"] == "$10K + $10K"


def test_next_growth_tier():
    tier = next_growth_tier(16_500)
    assert tier["current_daily_target"] == 200
    assert tier["current_weekly_target"] == 600
    assert tier["next_balance"] == 20_000
    assert tier["next_daily_target"] == 300
    assert tier["amount_to_next_tier"] == 3_500


def test_target_pct_for_dollars_on_10k():
    # need $150 net + $14 fees on ~$10k deploy ≈ 1.64%
    pct = target_pct_for_dollars(net_needed=150, deploy_dollar=10_000, fees=14)
    assert pct is not None
    assert 1.6 < pct < 1.7
