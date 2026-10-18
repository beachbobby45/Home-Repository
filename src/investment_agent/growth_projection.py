"""Tier-based growth plan projection for scenario visualizer / Plan tab.

Planning basis is the post-PDT $5K paper → staged RH funding path
(not the legacy $15K journal ORIGINAL_BASIS).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from investment_agent.finance import (
    DAILY_TARGET_EVERY,
    DAILY_TARGET_STEP,
    DEFAULT_MGMT_SWEEP_RATE,
    DEFAULT_TAX_RESERVE_RATE,
    GOAL_ACCOUNT_VALUE,
    SWEEP_SCHEDULE_ANNUAL,
    SWEEP_SCHEDULE_MONTHLY,
    TIER_LOT_STRUCTURES,
    capital_tier_detail,
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

# Plan tab / scenario planning start — matches paper ledger & RH Deposit #1
PLAN_STARTING_BASIS = 5_000.0
PLAN_FUNDED_TARGET = 20_000.0  # four × $5k invested under funding plan


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
class YearPlanRow:
    """One calendar year of the growth plan simulation."""

    year: int
    start_balance: float
    end_balance: float
    gross_production: float
    annual_sweep: float
    capital_injection: float
    trade_deploy_label: str
    trade_net_target: float
    tier_threshold: int
    goal_pct: float
    notes: str = ""


# Staged +$5K deposits after first $5K live (funding_plan.py earliest sketches).
# Cadence: ~30 trading sessions (~6 calendar weeks) between deposits.
# Offsets from RH Deposit #1 (2026-12-01 / plan week 0):
#   #2 ~2027-01-13 (week 6), #3 ~2027-02-25 (week 12), #4 ~2027-04-09 (week 18).
DEFAULT_FUNDING_INJECTIONS: tuple[CapitalInjection, ...] = (
    CapitalInjection(week_offset=6, amount=5_000.0, label="Deposit #2 (+$5K · ~2027-01-13)"),
    CapitalInjection(week_offset=12, amount=5_000.0, label="Deposit #3 (+$5K · ~2027-02-25)"),
    CapitalInjection(week_offset=18, amount=5_000.0, label="Deposit #4 (+$5K → $20K · ~2027-04-09)"),
)

# Backward-compatible alias: first scheduled deposit (tests / callers expecting one).
DEFAULT_INJECTION = DEFAULT_FUNDING_INJECTIONS[0]


def _tier_labels_at_balance(balance: float) -> tuple[str, float, int]:
    detail = capital_tier_detail(balance)
    return (
        detail["structure_label"],
        detail["trade_net_target"],
        int(detail["tier_threshold"]),
    )


def _simulate_yearly_plan(
    *,
    starting_balance: float = PLAN_STARTING_BASIS,
    years: int = 10,
    hit_rate: float = DEFAULT_HIT_RATE,
    tradeable_days_per_week: float = DEFAULT_TRADEABLE_DAYS_PER_WEEK,
    sweep_schedule: str = SWEEP_SCHEDULE_ANNUAL,
    tax_rate: float = DEFAULT_TAX_RESERVE_RATE,
    mgmt_rate: float = DEFAULT_MGMT_SWEEP_RATE,
    injections: tuple[CapitalInjection, ...] = (),
    goal: float = GOAL_ACCOUNT_VALUE,
) -> list[YearPlanRow]:
    """Run weekly simulation and emit one row per calendar year."""
    injection_map = {inj.week_offset: inj for inj in injections}
    balance = float(starting_balance)
    rows: list[YearPlanRow] = []
    total_weeks = years * WEEKS_PER_YEAR
    ytd_realized = 0.0
    week_in_year = 0
    year_gross = 0.0
    year_injection = 0.0
    year_sweep = 0.0
    year_start = balance
    calendar_year = 1
    goal_crossed = False

    for week in range(1, total_weeks + 1):
        daily = projection_daily_target(balance)
        weekly_net = round(daily * hit_rate * tradeable_days_per_week, 2)
        balance += weekly_net
        ytd_realized += weekly_net
        year_gross += weekly_net
        week_in_year += 1

        inj = injection_map.get(week)
        if inj:
            balance += inj.amount
            year_injection += inj.amount

        if week_in_year >= WEEKS_PER_YEAR:
            if sweep_schedule == SWEEP_SCHEDULE_ANNUAL:
                sweep = compute_period_end_sweep(ytd_realized, tax_rate=tax_rate, mgmt_rate=mgmt_rate)
                if sweep.applies:
                    balance -= sweep.total_sweep
                    year_sweep = sweep.total_sweep
                ytd_realized = 0.0
            deploy_label, net_trade, tier = _tier_labels_at_balance(balance)
            notes = ""
            if not goal_crossed and balance >= goal:
                notes = f"$5M goal crossed (~month {week // int(round(WEEKS_PER_MONTH))})"
                goal_crossed = True
            if year_injection > 0:
                notes = (notes + " · " if notes else "") + f"Capital in ${year_injection:,.0f}"
            rows.append(
                YearPlanRow(
                    year=calendar_year,
                    start_balance=round(year_start, 2),
                    end_balance=round(balance, 2),
                    gross_production=round(year_gross, 2),
                    annual_sweep=round(year_sweep, 2),
                    capital_injection=round(year_injection, 2),
                    trade_deploy_label=deploy_label,
                    trade_net_target=net_trade,
                    tier_threshold=tier,
                    goal_pct=round(goal_progress_pct(balance, goal=goal), 4),
                    notes=notes.strip(),
                )
            )
            calendar_year += 1
            week_in_year = 0
            year_gross = 0.0
            year_injection = 0.0
            year_sweep = 0.0
            year_start = balance

    return rows


def build_ten_year_growth_plan(
    *,
    years: int = 10,
    hit_rate: float = DEFAULT_HIT_RATE,
    tradeable_days_per_week: float = DEFAULT_TRADEABLE_DAYS_PER_WEEK,
    starting_balance: float = PLAN_STARTING_BASIS,
    injections: tuple[CapitalInjection, ...] | None = None,
    goal: float = GOAL_ACCOUNT_VALUE,
) -> dict:
    """
    Side-by-side Year 1–10 table: $5K base vs funded ladder to $20K invested.
    """
    inj_tuple = DEFAULT_FUNDING_INJECTIONS if injections is None else injections
    base_rows = _simulate_yearly_plan(
        starting_balance=starting_balance,
        years=years,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        injections=(),
        goal=goal,
    )
    inj_rows = _simulate_yearly_plan(
        starting_balance=starting_balance,
        years=years,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        injections=inj_tuple,
        goal=goal,
    )

    def _months_to_goal(rows: list[YearPlanRow]) -> int | None:
        for row in rows:
            if row.end_balance >= goal:
                return row.year * 12
        return None

    comparison: list[dict] = []
    for base, inj in zip(base_rows, inj_rows):
        comparison.append(
            {
                "year": base.year,
                "base": _year_row_to_dict(base),
                "injection": _year_row_to_dict(inj),
                "advantage_end_balance": round(inj.end_balance - base.end_balance, 2),
                "advantage_goal_pct": round(inj.goal_pct - base.goal_pct, 4),
            }
        )

    hit_pct = hit_rate * 100
    inj_total = sum(i.amount for i in inj_tuple)
    inj_label = (
        f"+${inj_total:,.0f} staged to ${PLAN_FUNDED_TARGET:,.0f}"
        if inj_tuple
        else "None"
    )
    inj_schedule = [
        {
            "week_offset": i.week_offset,
            "amount": i.amount,
            "label": i.label,
        }
        for i in inj_tuple
    ]

    cash_schedule = [
        {
            "stage": "RH Deposit #1 (CASH)",
            "date": "2026-12-01",
            "amount": starting_balance,
            "invested_after": starting_balance,
            "note": "After Oct–Nov paper pass · CASH/unlevered",
        },
        {
            "stage": "Deposit #2",
            "date": "2027-01-13",
            "amount": 5_000.0,
            "invested_after": 10_000.0,
            "note": "~30 sessions after #1 · evidence-gated",
        },
        {
            "stage": "Deposit #3",
            "date": "2027-02-25",
            "amount": 5_000.0,
            "invested_after": 15_000.0,
            "note": "~30 sessions after #2 · evidence-gated",
        },
        {
            "stage": "Deposit #4",
            "date": "2027-04-09",
            "amount": 5_000.0,
            "invested_after": PLAN_FUNDED_TARGET,
            "note": "~30 sessions after #3 → $20K invested · evidence-gated",
        },
    ]

    return {
        "goal": goal,
        "starting_basis": starting_balance,
        "funded_target": PLAN_FUNDED_TARGET,
        "assumptions": {
            "hit_rate_pct": round(hit_pct, 1),
            "tradeable_days_per_week": tradeable_days_per_week,
            "sweep_schedule": SWEEP_SCHEDULE_ANNUAL,
            "sweep_rate_pct": round((DEFAULT_MGMT_SWEEP_RATE + DEFAULT_TAX_RESERVE_RATE) * 100, 0),
            "capital_injection": inj_label,
            "injection_amount": inj_total,
            "injection_week": inj_tuple[0].week_offset if inj_tuple else None,
            "injection_schedule": inj_schedule,
            "cash_schedule": cash_schedule,
            "rh_live_date": "2026-12-01",
            "account_mode": "CASH / unlevered (no borrowed margin)",
            "sessions_per_week_cap": 5,
            "deposit_cadence": "+$5K every ~30 sessions after RH #1 until $20K invested",
            "one_trade_per_day": True,
            "second_trade": "Exceptional days only (#1 win + market GO)",
            "settlement": "Cash / unlevered · T+1 redeploy",
        },
        "months_to_goal": {
            "base": _months_to_goal(base_rows),
            "injection": _months_to_goal(inj_rows),
        },
        "years": comparison,
        "summary": (
            f"${starting_balance:,.0f} start (RH CASH #1 on 2026-12-01 after paper pass) · "
            f"{hit_pct:.1f}% hit · {tradeable_days_per_week:.1f} tradeable days/wk · "
            f"≤5 sessions/wk · 35% annual sweep. "
            f"+$5K ~every 30 sessions → $20K by ~2027-04-09 (gated). "
            f"With {inj_label}: "
            f"~{_months_to_goal(inj_rows) or '>120'} months to $5M vs "
            f"~{_months_to_goal(base_rows) or '>120'} base ($5K only)."
        ),
    }


def _year_row_to_dict(row: YearPlanRow) -> dict:
    return {
        "year": row.year,
        "start_balance": row.start_balance,
        "end_balance": row.end_balance,
        "gross_production": row.gross_production,
        "annual_sweep": row.annual_sweep,
        "capital_injection": row.capital_injection,
        "trade_deploy_label": row.trade_deploy_label,
        "trade_net_target": row.trade_net_target,
        "tier_threshold": row.tier_threshold,
        "goal_pct": row.goal_pct,
        "notes": row.notes,
    }


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
    starting_balance: float = PLAN_STARTING_BASIS,
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
    starting_balance: float = PLAN_STARTING_BASIS,
) -> dict[str, dict]:
    """Base $5K annual-sweep plan and staged funding ladder to $20K invested."""
    base_pts = project_growth_plan(
        starting_balance=starting_balance,
        months=months,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        sweep_schedule=SWEEP_SCHEDULE_ANNUAL,
    )
    injection_pts = project_growth_plan(
        starting_balance=starting_balance,
        months=months,
        hit_rate=hit_rate,
        tradeable_days_per_week=tradeable_days_per_week,
        sweep_schedule=SWEEP_SCHEDULE_ANNUAL,
        injections=DEFAULT_FUNDING_INJECTIONS,
    )
    hit_pct = hit_rate * 100
    return {
        "growth_plan_annual": projection_to_scenario_dict(
            base_pts,
            name="Growth plan ($5K · annual sweep)",
            description=(
                f"${starting_balance:,.0f} start · {hit_pct:.1f}% hit · "
                f"{tradeable_days_per_week:.1f} tradeable days/wk · ≤5 sessions/wk · "
                f"35% annual sweep."
            ),
        ),
        "growth_plan_injection": projection_to_scenario_dict(
            injection_pts,
            name="Growth plan (funded → $20K)",
            description=(
                f"Same as growth plan with +$5K every ~30 sessions to "
                f"${PLAN_FUNDED_TARGET:,.0f} invested "
                f"(#2 wk6 / #3 wk12 / #4 wk18 · {hit_pct:.1f}% hit · "
                f"annual 35% sweep · evidence-gated)."
            ),
        ),
    }


__all__ = [
    "CapitalInjection",
    "DEFAULT_FUNDING_INJECTIONS",
    "DEFAULT_HIT_RATE",
    "DEFAULT_INJECTION",
    "DEFAULT_TRADEABLE_DAYS_PER_WEEK",
    "GrowthProjectionPoint",
    "PLAN_FUNDED_TARGET",
    "PLAN_STARTING_BASIS",
    "YearPlanRow",
    "build_ten_year_growth_plan",
    "default_growth_scenarios",
    "months_to_goal_from_projection",
    "project_growth_plan",
    "projection_to_scenario_dict",
]
