"""Tier-based growth plan projection for scenario visualizer / Plan tab.

Planning basis is the Jan 4 2027 RH CASH $15k live seed (Dec 2026 paper
sized to match). Optional later deposits are evidence-gated, not scheduled.

Row 2026 is paper history from the gate ledger (actual trading P&L). It does
**not** carry into 2027 Begin — live seed is always a fresh $15k.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from typing import Any

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

# Plan tab / scenario planning start — matches $15k paper + Jan 4 2027 live seed
PLAN_STARTING_BASIS = 15_000.0
PLAN_FUNDED_TARGET = 15_000.0  # fresh seed; optional adds are evidence-gated
PLAN_START_CALENDAR_YEAR = 2027
# RH live 2027-01-04 → ~51 calendar weeks remain in 2027
PLAN_START_YEAR_WEEKS = 51
RH_LIVE_DATE = "2027-01-04"

# Informational paper-history row (Option A) — does not feed 2027 Begin
PAPER_HISTORY_YEAR = 2026
PAPER_HISTORY_START = 5_000.0


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


# No staged auto-ladder: live path is a single $15k seed on Jan 4 2027.
# Optional later capital stays evidence-gated (empty default schedule).
DEFAULT_FUNDING_INJECTIONS: tuple[CapitalInjection, ...] = ()

# Backward-compatible alias for callers expecting a CapitalInjection.
DEFAULT_INJECTION = CapitalInjection(
    week_offset=0, amount=0.0, label="(no staged deposits — $15k seed only)"
)


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
    start_calendar_year: int = PLAN_START_CALENDAR_YEAR,
    start_year_weeks: int = PLAN_START_YEAR_WEEKS,
    count_opening_deposit: bool = True,
) -> list[YearPlanRow]:
    """
    Weekly simulation bucketed by calendar year.

    Plan week 1 = first week on/after 2027-01-04. Calendar 2027 is a near-full
    year (~51 weeks); later years are full 52-week blocks. Annual 35% sweep
    applies at each calendar year-end.
    """
    injection_map = {inj.week_offset: inj for inj in injections if inj.amount}
    balance = float(starting_balance)
    rows: list[YearPlanRow] = []
    # Partial start year + (years - 1) full years
    total_weeks = start_year_weeks + max(years - 1, 0) * WEEKS_PER_YEAR
    ytd_realized = 0.0
    week_in_year = 0
    weeks_this_year = max(int(start_year_weeks), 1)
    year_gross = 0.0
    # Opening $15k counts as 2027 capital in (RH live seed)
    year_injection = float(starting_balance) if count_opening_deposit else 0.0
    year_sweep = 0.0
    year_start = balance
    calendar_year = int(start_calendar_year)
    goal_crossed = False
    goal_week: int | None = None

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

        if not goal_crossed and balance >= goal:
            goal_crossed = True
            goal_week = week

        if week_in_year >= weeks_this_year:
            if sweep_schedule == SWEEP_SCHEDULE_ANNUAL:
                sweep = compute_period_end_sweep(ytd_realized, tax_rate=tax_rate, mgmt_rate=mgmt_rate)
                if sweep.applies:
                    balance -= sweep.total_sweep
                    year_sweep = sweep.total_sweep
                ytd_realized = 0.0
            deploy_label, net_trade, tier = _tier_labels_at_balance(balance)
            notes_parts: list[str] = []
            if calendar_year == start_calendar_year:
                notes_parts.append(
                    "RH live Jan 4 · fresh $15K begin (paper equity does not transfer)"
                )
            if goal_crossed and goal_week is not None and goal_week > week - week_in_year:
                notes_parts.append(f"$5M goal crossed in {calendar_year}")
            if year_injection > 0:
                notes_parts.append(f"Capital in ${year_injection:,.0f}")
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
                    notes=" · ".join(notes_parts),
                )
            )
            calendar_year += 1
            week_in_year = 0
            weeks_this_year = WEEKS_PER_YEAR
            year_gross = 0.0
            year_injection = 0.0
            year_sweep = 0.0
            year_start = balance

    return rows


def build_paper_2026_history_row(
    conn: sqlite3.Connection | None = None,
    *,
    goal: float = GOAL_ACCOUNT_VALUE,
) -> dict[str, Any]:
    """Actual gate-book paper year for Plan row 2026 (does not feed 2027 Begin).

    Begin = historical $5k paper notional. Remaining = Begin + sum(fill net_pnl)
    so the Dec $15k top-up credit is excluded from “growth.”
    """
    begin = float(PAPER_HISTORY_START)
    fills = 0
    trading_pnl = 0.0
    if conn is not None:
        from investment_agent.execution.paper_ledger import (
            ACCOUNT_GATE,
            paper_scoreboard,
        )

        sb = paper_scoreboard(conn)
        arm = (sb.get("arms") or {}).get(ACCOUNT_GATE) or {}
        fills = int(arm.get("fills") or 0)
        trading_pnl = float(arm.get("total_net_pnl") or 0.0)

    remaining = round(begin + trading_pnl, 2)
    growth = round(trading_pnl, 2)
    detail = capital_tier_detail(begin)
    notes = (
        f"Paper (gate) · {fills} fills · trading P&L ${growth:+,.2f} · "
        "does not transfer to 2027 Begin"
    )
    row = YearPlanRow(
        year=PAPER_HISTORY_YEAR,
        start_balance=begin,
        end_balance=remaining,
        gross_production=growth,
        annual_sweep=0.0,
        capital_injection=0.0,
        trade_deploy_label=detail["structure_label"],
        trade_net_target=float(detail["trade_net_target"]),
        tier_threshold=int(detail["tier_threshold"]),
        goal_pct=round(goal_progress_pct(remaining, goal=goal), 4),
        notes=notes,
    )
    payload = _year_row_to_dict(row)
    return {
        "year": PAPER_HISTORY_YEAR,
        "base": payload,
        "injection": payload,
        "advantage_end_balance": 0.0,
        "advantage_goal_pct": 0.0,
        "is_paper_history": True,
    }


def build_ten_year_growth_plan(
    *,
    years: int = 12,
    hit_rate: float = DEFAULT_HIT_RATE,
    tradeable_days_per_week: float = DEFAULT_TRADEABLE_DAYS_PER_WEEK,
    starting_balance: float = PLAN_STARTING_BASIS,
    injections: tuple[CapitalInjection, ...] | None = None,
    goal: float = GOAL_ACCOUNT_VALUE,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """
    Calendar-year table: 2026 paper history + 2027–… live $15K seed path.

    2027 Begin is always ``starting_balance`` ($15k) — never 2026 Remaining.
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

    def _goal_calendar_year(rows: list[YearPlanRow]) -> int | None:
        for row in rows:
            if row.end_balance >= goal:
                return row.year
        return None

    def _months_to_goal(rows: list[YearPlanRow]) -> int | None:
        """Approximate months from Jan 2027 plan start to year-end when goal is hit."""
        gy = _goal_calendar_year(rows)
        if gy is None:
            return None
        if gy <= PLAN_START_CALENDAR_YEAR:
            return 12
        return (gy - PLAN_START_CALENDAR_YEAR + 1) * 12

    comparison: list[dict] = []
    # Row 1: paper history (actual). Explicitly does not seed the live sim below.
    paper_row = build_paper_2026_history_row(conn, goal=goal)
    comparison.append(paper_row)

    for base, inj in zip(base_rows, inj_rows):
        comparison.append(
            {
                "year": base.year,
                "base": _year_row_to_dict(base),
                "injection": _year_row_to_dict(inj),
                "advantage_end_balance": round(inj.end_balance - base.end_balance, 2),
                "advantage_goal_pct": round(inj.goal_pct - base.goal_pct, 4),
                "is_paper_history": False,
            }
        )

    hit_pct = hit_rate * 100
    inj_total = sum(i.amount for i in inj_tuple)
    inj_label = (
        f"+${inj_total:,.0f} optional staged (evidence-gated)"
        if inj_tuple
        else "None — $15k seed only"
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
            "stage": "2026 paper history (gate book)",
            "date": "2026-10-20",
            "amount": 0.0,
            "invested_after": 0.0,
            "note": (
                f"Begin ${PAPER_HISTORY_START:,.0f} · Remaining = begin + trading P&L · "
                "does not transfer to 2027"
            ),
        },
        {
            "stage": "Dec paper at $15k sizing",
            "date": "2026-12-01",
            "amount": 0.0,
            "invested_after": 0.0,
            "note": "Paper mode · top-up preserves fills · ~$225/trade",
        },
        {
            "stage": "RH live $15k CASH seed",
            "date": RH_LIVE_DATE,
            "amount": starting_balance,
            "invested_after": starting_balance,
            "note": "Fresh seed — 2027 Begin is exactly $15k (not 2026 Remaining)",
        },
    ]

    goal_year_base = _goal_calendar_year(base_rows)
    goal_year_inj = _goal_calendar_year(inj_rows)
    paper_remaining = float(paper_row["injection"]["end_balance"])

    return {
        "goal": goal,
        "starting_basis": starting_balance,
        "funded_target": PLAN_FUNDED_TARGET,
        "calendar_year_start": PAPER_HISTORY_YEAR,
        "live_start_year": PLAN_START_CALENDAR_YEAR,
        "paper_history_year": PAPER_HISTORY_YEAR,
        "paper_history_start": PAPER_HISTORY_START,
        "paper_history_remaining": paper_remaining,
        "calendar_year_end": (
            comparison[-1]["year"] if comparison else PLAN_START_CALENDAR_YEAR
        ),
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
            "rh_live_date": RH_LIVE_DATE,
            "account_mode": "CASH / unlevered (no borrowed margin)",
            "sessions_per_week_cap": 5,
            "deposit_cadence": (
                "2026 = paper history · 2027 Begin = fresh $15k on 2027-01-04 "
                "(paper Remaining does not carry)"
            ),
            "trade_net_target_pct": 1.50,
            "one_trade_per_day": True,
            "second_trade": "Exceptional days only (#1 win + market GO)",
            "settlement": "Cash / unlevered · T+1 redeploy · live same-day EOD flatten",
            "year_axis": "calendar",
            "paper_does_not_transfer": True,
        },
        "months_to_goal": {
            "base": _months_to_goal(base_rows),
            "injection": _months_to_goal(inj_rows),
        },
        "goal_year": {
            "base": goal_year_base,
            "injection": goal_year_inj,
        },
        "years": comparison,
        "summary": (
            f"2026 paper (gate): ${PAPER_HISTORY_START:,.0f} → "
            f"${paper_remaining:,.2f} trading P&L only — does not transfer. "
            f"2027 Begin = ${starting_balance:,.0f} exactly (RH CASH live {RH_LIVE_DATE}). "
            f"{hit_pct:.1f}% hit · {tradeable_days_per_week:.1f} tradeable days/wk · "
            f"≤5 sessions/wk · 35% annual sweep · ~1.50% net/trade. "
            f"$5M target: ~{goal_year_inj or goal_year_base or 'beyond table'}."
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
    """Base $15K annual-sweep plan (optional staged adds when configured)."""
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
            name="Growth plan ($15K · annual sweep)",
            description=(
                f"${starting_balance:,.0f} start ({RH_LIVE_DATE}) · {hit_pct:.1f}% hit · "
                f"{tradeable_days_per_week:.1f} tradeable days/wk · ≤5 sessions/wk · "
                f"35% annual sweep · ~1.50% net/trade."
            ),
        ),
        "growth_plan_injection": projection_to_scenario_dict(
            injection_pts,
            name="Growth plan ($15K seed)",
            description=(
                f"Same $15k seed path"
                + (
                    f" with optional staged adds to ${PLAN_FUNDED_TARGET:,.0f}"
                    if DEFAULT_FUNDING_INJECTIONS
                    else " (no staged deposits)"
                )
                + f" · {hit_pct:.1f}% hit · annual 35% sweep."
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
    "PAPER_HISTORY_START",
    "PAPER_HISTORY_YEAR",
    "PLAN_FUNDED_TARGET",
    "PLAN_START_CALENDAR_YEAR",
    "PLAN_START_YEAR_WEEKS",
    "PLAN_STARTING_BASIS",
    "RH_LIVE_DATE",
    "YearPlanRow",
    "build_paper_2026_history_row",
    "build_ten_year_growth_plan",
    "default_growth_scenarios",
    "months_to_goal_from_projection",
    "project_growth_plan",
    "projection_to_scenario_dict",
]
