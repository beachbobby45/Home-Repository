"""Tests for dollar-target prediction and historical simulation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.dollar_target import (
    DollarDayBar,
    assess_dollar_reachability,
    evaluate_dollar_history,
    estimate_net_at_typical_high,
    net_at_high_from_open,
    simulate_dollar_outcome,
)
from investment_agent.finance import ORIGINAL_BASIS


def test_adp_aug7_not_reachable_from_open():
    """ADP 2026-08-07 — high ~+0.85% could not deliver $150 net from open."""
    open_px = 272.95
    high = 275.27
    low = 271.50
    deploy = 10_000.0
    outcome = simulate_dollar_outcome(open_px, high, low, deploy_dollar=deploy, net_target=150.0)
    assert outcome == "neither"
    net_high = net_at_high_from_open(open_px, high, deploy_dollar=deploy)
    assert net_high < 150.0
    assert net_high == 69.52

    pred = assess_dollar_reachability(
        entry_price=open_px,
        deploy_dollar=deploy,
        net_target=150.0,
        avg_range_pct=2.4,
    )
    assert pred["verdict"] == "NOT_REACHABLE"
    assert pred["expected_net_at_typical_high"] is not None
    assert pred["expected_net_at_typical_high"] < 150.0


def test_dollar_history_hit_rate():
    """Three days: one hits $150 from open, one stops, one neither."""
    bars = [
        DollarDayBar(open=100.0, high=103.0, low=99.5),   # likely target at ~101.5+
        DollarDayBar(open=100.0, high=100.5, low=99.0),   # stop
        DollarDayBar(open=50.0, high=50.4, low=49.9),     # neither on $10K
    ]
    stats = evaluate_dollar_history(bars, deploy_dollar=10_000.0, net_target=150.0)
    assert stats.days_evaluated == 3
    assert stats.dollar_targets >= 1
    assert stats.dollar_hit_rate_pct >= 0


def test_estimate_net_at_typical_high():
    net = estimate_net_at_typical_high(
        100.0,
        avg_range_pct=3.0,
        deploy_dollar=10_000.0,
    )
    assert net > 0
    assert net == 134.5


def test_high_enough_reaches_target():
    open_px = 100.0
    high = 102.5
    low = 99.5
    outcome = simulate_dollar_outcome(
        open_px, high, low, deploy_dollar=10_000.0, net_target=150.0,
    )
    assert outcome == "target"
