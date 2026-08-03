"""Financial model: fees, goal progress, month-end sweeps (v3)."""

from __future__ import annotations

from dataclasses import dataclass

# Defaults from approved product spec v3
ORIGINAL_BASIS = 10_000.0
GOAL_ACCOUNT_VALUE = 5_000_000.0
DEFAULT_BUY_FEE = 7.0
DEFAULT_SELL_FEE = 7.0
DEFAULT_TAX_RESERVE_RATE = 0.25
DEFAULT_MGMT_SWEEP_RATE = 0.10

# Scalable daily net profit target (v3.1 operating plan)
DAILY_TARGET_BASE = 150.0  # at $10K basis
DAILY_TARGET_STEP = 50.0  # added per tier
DAILY_TARGET_EVERY = 5_000.0  # balance step between tiers
DAILY_TARGET_MILESTONE_GOAL = 350.0  # full daily goal at $20K+
DAILY_TARGET_MILESTONE_AT = 20_000.0


@dataclass(frozen=True)
class MonthEndSweep:
    """Sweeps applied only when monthly realized net profit is positive."""

    monthly_realized_net: float
    management_sweep: float
    tax_sweep: float
    total_sweep: float

    @property
    def applies(self) -> bool:
        return self.monthly_realized_net > 0


def round_trip_fees(
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    return buy_fee + sell_fee


def goal_progress_pct(
    tradable_balance: float,
    goal: float = GOAL_ACCOUNT_VALUE,
) -> float:
    if goal <= 0:
        return 0.0
    return (tradable_balance / goal) * 100.0


def compute_month_end_sweep(
    monthly_realized_net: float,
    tax_rate: float = DEFAULT_TAX_RESERVE_RATE,
    mgmt_rate: float = DEFAULT_MGMT_SWEEP_RATE,
) -> MonthEndSweep:
    """
    10% management + tax reserve on positive monthly realized net only.
    During the month, tradable cash is unchanged by this calculation;
    sweeps are applied at month-end on the trading account.
    """
    if monthly_realized_net <= 0:
        return MonthEndSweep(
            monthly_realized_net=monthly_realized_net,
            management_sweep=0.0,
            tax_sweep=0.0,
            total_sweep=0.0,
        )
    mgmt = monthly_realized_net * mgmt_rate
    tax = monthly_realized_net * tax_rate
    return MonthEndSweep(
        monthly_realized_net=monthly_realized_net,
        management_sweep=mgmt,
        tax_sweep=tax,
        total_sweep=mgmt + tax,
    )


def tradable_after_sweep(
    tradable_balance_before_sweep: float,
    sweep: MonthEndSweep,
) -> float:
    return tradable_balance_before_sweep - sweep.total_sweep


def daily_profit_target(
    tradable_balance: float,
    *,
    base: float = DAILY_TARGET_BASE,
    step: float = DAILY_TARGET_STEP,
    every: float = DAILY_TARGET_EVERY,
    basis: float = ORIGINAL_BASIS,
) -> float:
    """
    Daily net profit goal: $150 at $10K, +$50 for each additional $5K balance.
    $10K→$150, $15K→$200, $20K→$250, … reaching $350/day at $20K in the scaling example
    (use milestone note when marketing the $350 tier at $20K).
    """
    tiers = max(int((tradable_balance - basis) // every), 0)
    return base + tiers * step


def growth_plan_milestones(
    *,
    basis: float = ORIGINAL_BASIS,
    step_balance: float = DAILY_TARGET_EVERY,
    max_balance: float = 50_000.0,
) -> list[dict]:
    """Balance tiers and daily targets for dashboard growth table."""
    rows: list[dict] = []
    balance = basis
    while balance <= max_balance:
        rows.append(
            {
                "balance_at_least": balance,
                "daily_target": daily_profit_target(balance),
            }
        )
        balance += step_balance
    return rows


def next_growth_tier(tradable_balance: float) -> dict:
    """Current daily target and the next balance milestone."""
    tiers = max(int((tradable_balance - ORIGINAL_BASIS) // DAILY_TARGET_EVERY), 0)
    next_balance = ORIGINAL_BASIS + (tiers + 1) * DAILY_TARGET_EVERY
    return {
        "current_daily_target": daily_profit_target(tradable_balance),
        "current_tier_balance": ORIGINAL_BASIS + tiers * DAILY_TARGET_EVERY,
        "next_balance": next_balance,
        "next_daily_target": daily_profit_target(next_balance),
        "amount_to_next_tier": max(round(next_balance - tradable_balance, 2), 0.0),
        "milestone_daily_350_at": DAILY_TARGET_MILESTONE_AT,
    }
