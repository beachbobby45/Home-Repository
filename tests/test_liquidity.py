"""Tests for liquidity metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.liquidity import DailyBar, compute_liquidity_metrics, daily_range_pct


def _bars(range_pct: float, days: int = 20) -> list[DailyBar]:
    close = 100.0
    half = (range_pct / 100.0) * close / 2.0
    return [
        DailyBar(high=close + half, low=close - half, close=close, volume=500_000)
        for _ in range(days)
    ]


def test_daily_range_pct():
    bar = DailyBar(high=103.0, low=97.0, close=100.0, volume=1)
    assert abs(daily_range_pct(bar) - 6.0) < 0.01


def test_near_swing_target_at_three_percent():
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=10_000)
    assert metrics.near_swing_target is True
    assert metrics.avg_range_pct == 3.0


def test_liquidity_cap_respects_tradable_cash():
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=5_000)
    assert metrics.liquidity_cap <= 5_000


def test_meets_liquidity_min():
    # 500k shares * $100 = $50M ADV
    metrics = compute_liquidity_metrics(_bars(3.0), tradable_cash=10_000)
    assert metrics.meets_liquidity_min is True
