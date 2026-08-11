"""Tests for dollar-goal rank gate and tightened scoring weights."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.dollar_target import (
    MIN_RANK_AVG_NET_RATIO,
    MIN_RANK_DOLLAR_HIT_RATE_PCT,
    passes_dollar_rank_gate,
)
from investment_agent.period_screener import RANK_WEIGHTS, _criteria_likelihood_score


def test_rank_weights_sum_to_one():
    assert abs(sum(RANK_WEIGHTS.values()) - 1.0) < 1e-9


def test_passes_dollar_rank_gate_requires_hit_rate_and_avg_net():
    assert passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=140.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=30.0,
        avg_net_at_high=160.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=120.0,
        net_target=150.0,
        days_screened=5,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=50.0,
        avg_net_at_high=200.0,
        net_target=200.0,
        days_screened=1,
    )


def test_scoring_prefers_strong_dollar_history():
    strong = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=60.0,
        dollar_hit_rate_pct=70.0,
        avg_net_at_high=170.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    weak = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=80.0,
        dollar_hit_rate_pct=20.0,
        avg_net_at_high=80.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    assert strong["score"] > weak["score"]
    assert strong["dollar_avg_net_component"] > weak["dollar_avg_net_component"]


def test_net_target_scales_gate_threshold():
    net_target = 200.0
    min_avg = net_target * MIN_RANK_AVG_NET_RATIO
    assert passes_dollar_rank_gate(
        dollar_hit_rate_pct=MIN_RANK_DOLLAR_HIT_RATE_PCT,
        avg_net_at_high=min_avg,
        net_target=net_target,
        days_screened=3,
    )
    assert not passes_dollar_rank_gate(
        dollar_hit_rate_pct=MIN_RANK_DOLLAR_HIT_RATE_PCT,
        avg_net_at_high=min_avg - 1,
        net_target=net_target,
        days_screened=3,
    )
