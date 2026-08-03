"""Tests for strategy models and daily profit targets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.strategy_models import (
    daily_profit_target,
    target_pct_for_dollars,
)


def test_daily_profit_target_scales_every_5k():
    assert daily_profit_target(10_000) == 350
    assert daily_profit_target(14_999) == 350
    assert daily_profit_target(15_000) == 400
    assert daily_profit_target(20_000) == 450


def test_target_pct_for_dollars_on_10k():
    # need $350 net + $14 fees on ~$10k deploy
    pct = target_pct_for_dollars(net_needed=350, deploy_dollar=10_000, fees=14)
    assert pct is not None
    assert 3.5 < pct < 3.8
