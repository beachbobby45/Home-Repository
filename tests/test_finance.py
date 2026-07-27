"""Tests for v3 financial model."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import (
    GOAL_ACCOUNT_VALUE,
    compute_month_end_sweep,
    goal_progress_pct,
    round_trip_fees,
    tradable_after_sweep,
)


def test_round_trip_fees():
    assert round_trip_fees() == 14.0


def test_goal_progress_pct():
    assert goal_progress_pct(10_700) == (10_700 / GOAL_ACCOUNT_VALUE) * 100


def test_sweep_zero_on_loss_month():
    sweep = compute_month_end_sweep(-500.0)
    assert not sweep.applies
    assert sweep.total_sweep == 0.0


def test_sweep_on_gain_month():
    sweep = compute_month_end_sweep(1000.0)
    assert sweep.management_sweep == 100.0
    assert sweep.tax_sweep == 250.0
    assert sweep.total_sweep == 350.0


def test_tradable_after_sweep():
    sweep = compute_month_end_sweep(1000.0)
    assert tradable_after_sweep(11_000.0, sweep) == 10_650.0


def test_editable_tax_rate():
    sweep = compute_month_end_sweep(1000.0, tax_rate=0.30)
    assert sweep.tax_sweep == 300.0
