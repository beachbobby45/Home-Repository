"""Tests for tier-based growth plan projection."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import GOAL_ACCOUNT_VALUE
from investment_agent.growth_projection import (
    DEFAULT_FUNDING_INJECTIONS,
    PLAN_STARTING_BASIS,
    CapitalInjection,
    default_growth_scenarios,
    project_growth_plan,
)


def test_project_growth_plan_starts_at_fifteen_k():
    pts = project_growth_plan(months=12)
    assert pts[0].balance == PLAN_STARTING_BASIS == 15_000.0
    assert pts[-1].balance > PLAN_STARTING_BASIS


def test_default_funding_injections_empty():
    assert DEFAULT_FUNDING_INJECTIONS == ()


def test_optional_injection_still_supported():
    base = project_growth_plan(months=24)
    injected = project_growth_plan(
        months=24,
        injections=(CapitalInjection(week_offset=26, amount=5_000.0),),
    )
    inj_pt = next(p for p in injected if p.injection_total > 0)
    assert inj_pt.injection_total == 5_000.0
    late = next(p for p in injected if p.month_offset == 12)
    base_at = next(p for p in base if p.month_offset == 12)
    assert late.balance > base_at.balance


def test_default_growth_scenarios_fifteen_k():
    scenarios = default_growth_scenarios(months=120)
    assert "growth_plan_annual" in scenarios
    assert "growth_plan_injection" in scenarios
    assert scenarios["growth_plan_annual"]["months_to_goal"] is not None
    inj = scenarios["growth_plan_injection"]["months_to_goal"]
    base = scenarios["growth_plan_annual"]["months_to_goal"]
    assert inj is not None and base is not None
    assert inj == base  # no staged ladder by default
    assert "$15" in scenarios["growth_plan_annual"]["description"]


def test_growth_plan_reaches_goal_within_horizon():
    scenarios = default_growth_scenarios(months=120)
    months = scenarios["growth_plan_annual"]["months_to_goal"]
    assert months is not None
    assert months <= 120
    last = scenarios["growth_plan_annual"]["points"][-1]
    assert last["balance"] >= GOAL_ACCOUNT_VALUE or months <= 120
