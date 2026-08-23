"""Tier-based growth plan projection for scenario visualizer."""

from __future__ import annotations

import math
from dataclasses import dataclass

from investment_agent.finance import (
    DAILY_TARGET_EVERY,
    DAILY_TARGET_STEP,
    DEFAULT_MGMT_SWEEP_RATE,
    DEFAULT_TAX_RESERVE_RATE,
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    SWEEP_SCHEDULE_ANNUAL,
    SWEEP_SCHEDULE_MONTHLY,
    TIER_LOT_STRUCTURES,
    compute_period_end_sweep,
    daily_profit_target,
    goal_progress_pct,
)

# Operating assumptions from period screener / relaxed market-activity gate
DEFAULT_HIT_RATE = 0.606
DEFAULT_TRADEABLE_DAYS_PER_WEEK = 2.9
WEEKS_PER_YEAR = 52
WEEKS_PER_MONTH = WEEKS_PER_YEAR / 12.0
_MAX_TIER_THRESHOLD = max(TIER_LOT_STRUCTURES.keys())


def projection_daily_target(balance: float) -> float:
    """
    Daily production for scenario modeling.

    Uses split-lot tiers through $60K, then +$50/day per additional $5K equity
    (same step as ``LOT_DAILY_STEP`` / legacy tier ladder).
    """
    if balance <= _MAX_TIER_THRESHOLD:
        return daily_profit_target(balance)
    base = daily_profit_target(float(_MAX_TIER_THRESHOLD))
    extra_steps = int((balance - _MAX_TIER_THRESHOLD) // DAILY_TARGET_EVERY)
    return round(base + extra_steps * DAILY_TARGET_STEP, 2)


@dataclass(frozen=True)
class CapitalInjection:
    """One-time capital add at a week offset from plan start."""

    week_offset: int
    amount: float
    label: str = ""


@dataclass(frozen=True)
class GrowthProjectionPoint:
    month_offset: int
    balance: float
    goal_pct: float
    weekly_net: float
    sweep_total: float
    injection_total: float


def _annual_sweep_key(year_index: int, start_year: int = 1) -> str:
    return f"{start_year + year_index - 1}-annual"


def project_growth_plan(
    *,
    starting_balance: float = ORIGINAL_BASIS,
    months: int = 120,
    hit_rate: float = DEFAULT_HIT_RATE,
    tradeable_days_per_week: float = DEFAULT_TRADEABLE_DAYS_PER_WEEK,
    sweep_schedule: str = SWEEP_SCHEDULE_ANNUAL,
    tax_rate: float = DEFAULT_TAX_RESERVE_RATE,
    mgmt_rate: float = DEFAULT_MGMT_SWEEP_RATE,
    injections: tuple[CapitalInjection, ...] = (),
    goal: float = GOAL_ACCOUNT_VALUE,
) -> list[GrowthProjectionPoint]:
    """
    Simulate tier-scaled production with configurable sweep schedule.

    Weekly expected net = daily tier target × hit rate × tradeable days/week.
    Annual mode sweeps 35% of YTD realized net at each 52-week boundary.
    """
    total_weeks = max(int(math.ceil(months * WEEKS_PER_MONTH)), 1)
    balance = float(starting_balance)
    injection_map = {inj.week_offset: inj for inj in injections}

    points: list[GrowthProjectionPoint] = [
        GrowthProjectionPoint(
            month_offset=0,
            balance=round(balance, 2),
            goal_pct=goal_progress_pct(balance, goal=goal),
            weekly_net=0.0,
            sweep_total=0.0,
            injection_total=0.0,
        )
    ]

    ytd_realized = 0.0
    week_in_year = 0
    month_idx = 0
    weeks_in_current_month = 0.0
    month_injection = 0.0

    for week in range(1, total_weeks + 1):
        daily = projection_daily_target(balance)
        weekly_net = round(daily * hit_rate * tradeable_days_per_week, 2)
        balance += weekly_net
        ytd_realized += weekly_net
        week_in_year += 1
        weeks_in_current_month += 1

        injection_total = 0.0
        inj = injection_map.get(week)
        if inj:
            balance += inj.amount
            injection_total = inj.amount
            month_injection += inj.amount

        sweep_total = 0.0
        is_year_end = week_in_year >= WEEKS_PER_YEAR
        end_of_month = weeks_in_current_month >= WEEKS_PER_MONTH

        if sweep_schedule == SWEEP_SCHEDULE_ANNUAL and is_year_end:
            sweep = compute_period_end_sweep(ytd_realized, tax_rate=tax_rate, mgmt_rate=mgmt_rate)
            if sweep.applies:
                balance -= sweep.total_sweep
                sweep_total = sweep.total_sweep
            ytd_realized = 0.0
            week_in_year = 0
        elif sweep_schedule == SWEEP_SCHEDULE_MONTHLY and end_of_month:
            sweep = compute_period_end_sweep(ytd_realized, tax_rate=tax_rate, mgmt_rate=mgmt_rate)
            if sweep.applies:
                balance -= sweep.total_sweep
                sweep_total = sweep.total_sweep
            ytd_realized = 0.0

        if end_of_month:
            month_idx += 1
            weeks_in_current_month = 0.0
            points.append(
                GrowthProjectionPoint(
                    month_offset=month_idx,
                    balance=round(balance, 2),
                    goal_pct=goal_progress_pct(balance, goal=goal),
                    weekly_net=weekly_net,
                    sweep_total=sweep_total,
                    injection_total=round(month_injection, 2),
                )
            )
            month_injection = 0.0

    while len(points) <= months:
        month_idx += 1
        points.append(
            GrowthProjectionPoint(
                month_offset=month_idx,
                balance=round(balance, 2),
                goal_pct=goal_progress_pct(balance, goal=goal),
                weekly_net=0.0,
                sweep_total=0.0,
                injection_total=0.0,
            )
        )

    return points[: months + 1]


def months_to_goal_from_projection(points: list[GrowthProjectionPoint], goal: float = GOAL_ACCOUNT_VALUE) -> float | None:
    for pt in points:
        if pt.balance >= goal:
            return float(pt.month_offset)
    return None


def projection_to_scenario_dict(
    points: list[GrowthProjectionPoint],
    *,
    name: str,
    description: str,
    goal: float = GOAL_ACCOUNT_VALUE,
) -> dict:
    months_to = months_to_goal_from_projection(points, goal=goal)
    return {
        "name": name,
        "description": description,
        "months_to_goal": months_to,
        "reachable": months_to is not None,
        "points": [
            {
                "month_offset": p.month_offset,
                "balance": p.balance,
                "goal_pct": p.goal_pct,
            }
            for p in points
        ],
    }


def default_growth_scenarios(
    *,
    months: int = 120,
    hit_rate: float = DEFAULT_HIT_RATE,
    tradeable_days_per_week: float = DEFAULT_TRADEABLE_DAYS_PER_WEEK,
) -> dict[str, dict]:
    """Base $15K annual-sweep plan and +$10K injection at week 26 (~6 months)."""
    base_pts = project_growth_plan(
        months=months,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        sweep_schedule=SWEEP_SCHEDULE_ANNUAL,
    )
    injection_pts = project_growth_plan(
        months=months,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        sweep_schedule=SWEEP_SCHEDULE_ANNUAL,
        injections=(CapitalInjection(week_offset=26, amount=10_000.0, label="+$10K @ ~6 mo"),),
    )
    hit_pct = hit_rate * 100
    return {
        "growth_plan_annual": projection_to_scenario_dict(
            base_pts,
            name="Growth plan (annual sweep)",
            description=(
                f"${ORIGINAL_BASIS:,.0f} start · {hit_pct:.1f}% hit · "
                f"{tradeable_days_per_week:.1f} tradeable days/wk · 35% annual sweep."
            ),
        ),
        "growth_plan_injection": projection_to_scenario_dict(
            injection_pts,
            name="Growth plan (+$10K @ 6 mo)",
            description=(
                f"Same as growth plan with +$10,000 capital injection at week 26 "
                f"({hit_pct:.1f}% hit · annual 35% sweep)."
            ),
        ),
    }


__all__ = [
    "CapitalInjection",
    "DEFAULT_HIT_RATE",
    "DEFAULT_TRADEABLE_DAYS_PER_WEEK",
    "GrowthProjectionPoint",
    "default_growth_scenarios",
    "months_to_goal_from_projection",
    "project_growth_plan",
    "projection_to_scenario_dict",
]
