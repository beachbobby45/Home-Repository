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

# Scalable daily net profit target (v3.1 operating plan — superseded by split-lot model Inc 10)
DAILY_TARGET_BASE = 150.0  # at $10K basis
DAILY_TARGET_STEP = 50.0  # added per tier (legacy linear model)
DAILY_TARGET_EVERY = 5_000.0  # balance step between tiers (legacy)
DAILY_TARGET_MILESTONE_GOAL = 350.0  # legacy reference
DAILY_TARGET_MILESTONE_AT = 20_000.0

# Phase 1B split-lot production model
WEEKLY_PRODUCTION_OPPORTUNITIES = 3
LOT_BASE_SIZE = 10_000.0
LOT_SIZE_STEP = 5_000.0
LOT_DAILY_BASE = 150.0
LOT_DAILY_STEP = 50.0

# Tier threshold (equity) → virtual lot sizes (sum equals threshold at milestones)
TIER_LOT_STRUCTURES: dict[int, tuple[int, ...]] = {
    10_000: (10_000,),
    15_000: (15_000,),
    20_000: (10_000, 10_000),
    25_000: (10_000, 15_000),
    30_000: (15_000, 15_000),
    35_000: (15_000, 20_000),
    40_000: (20_000, 20_000),
    45_000: (20_000, 25_000),
    50_000: (25_000, 25_000),
    55_000: (25_000, 30_000),
    60_000: (30_000, 30_000),
}


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


def sell_price_for_net_target(
    *,
    entry_price: float,
    shares: int,
    net_target: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    """Limit price where selling ``shares`` nets ``net_target`` after round-trip fees."""
    if entry_price <= 0 or shares <= 0 or net_target <= 0:
        return entry_price
    gross_needed = net_target + buy_fee + sell_fee
    return entry_price + gross_needed / shares


def target_move_pct(entry_price: float, target_price: float) -> float:
    if entry_price <= 0:
        return 0.0
    return ((target_price - entry_price) / entry_price) * 100.0


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


def lot_daily_production(lot_size: float) -> float:
    """Daily net production rate for one virtual lot (e.g. $10K lot → $150)."""
    size = max(float(lot_size), LOT_BASE_SIZE)
    steps = (size - LOT_BASE_SIZE) / LOT_SIZE_STEP
    return round(LOT_DAILY_BASE + steps * LOT_DAILY_STEP, 2)


def tier_threshold_for_equity(
    equity: float,
    *,
    basis: float = ORIGINAL_BASIS,
) -> int:
    """Highest tier milestone at or below ``equity``."""
    if equity < basis:
        return int(basis)
    thresholds = sorted(TIER_LOT_STRUCTURES.keys())
    selected = thresholds[0]
    for threshold in thresholds:
        if equity >= threshold:
            selected = threshold
        else:
            break
    return selected


def split_lot_structure(
    equity: float,
    *,
    basis: float = ORIGINAL_BASIS,
) -> tuple[int, ...]:
    """Virtual lot breakdown for Capital Builder tier at ``equity``."""
    key = tier_threshold_for_equity(equity, basis=basis)
    return TIER_LOT_STRUCTURES[key]


def _format_lot_label(lot_size: int) -> str:
    if lot_size % 1000 == 0:
        return f"${lot_size // 1000}K"
    return f"${lot_size:,.0f}"


def capital_tier_detail(
    equity: float,
    *,
    basis: float = ORIGINAL_BASIS,
) -> dict:
    """Split-lot tier breakdown for dashboard and trade sizing."""
    lots = split_lot_structure(equity, basis=basis)
    lot_rows = [
        {"lot_size": lot, "daily_rate": lot_daily_production(lot)}
        for lot in lots
    ]
    daily = round(sum(row["daily_rate"] for row in lot_rows), 2)
    weekly = round(daily * WEEKLY_PRODUCTION_OPPORTUNITIES, 2)
    return {
        "tier_threshold": tier_threshold_for_equity(equity, basis=basis),
        "lot_structure": list(lots),
        "lots": lot_rows,
        "daily_production_target": daily,
        "weekly_production_target": weekly,
        "weekly_opportunities": WEEKLY_PRODUCTION_OPPORTUNITIES,
        "structure_label": " + ".join(_format_lot_label(lot) for lot in lots),
        "per_opportunity_target": daily,
    }


def weekly_production_target(
    tradable_balance: float,
    *,
    basis: float = ORIGINAL_BASIS,
) -> float:
    """Weekly guidance = 3 × daily production at current tier."""
    return capital_tier_detail(tradable_balance, basis=basis)["weekly_production_target"]


def daily_profit_target(
    tradable_balance: float,
    *,
    base: float = DAILY_TARGET_BASE,
    step: float = DAILY_TARGET_STEP,
    every: float = DAILY_TARGET_EVERY,
    basis: float = ORIGINAL_BASIS,
) -> float:
    """
    Daily net production goal from split-lot tier (Phase 1B).

    Legacy linear args (base/step/every) are ignored — kept for call-site compatibility.
    """
    _ = (base, step, every)
    return capital_tier_detail(tradable_balance, basis=basis)["daily_production_target"]


def growth_plan_milestones(
    *,
    basis: float = ORIGINAL_BASIS,
    step_balance: float = DAILY_TARGET_EVERY,
    max_balance: float = 50_000.0,
) -> list[dict]:
    """Capital Builder tier table for dashboard growth reference."""
    _ = step_balance
    rows: list[dict] = []
    for threshold in sorted(TIER_LOT_STRUCTURES.keys()):
        if threshold < basis or threshold > max_balance:
            continue
        detail = capital_tier_detail(float(threshold), basis=basis)
        rows.append(
            {
                "balance_at_least": float(threshold),
                "daily_target": detail["daily_production_target"],
                "weekly_target": detail["weekly_production_target"],
                "lot_structure": detail["lot_structure"],
                "structure_label": detail["structure_label"],
            }
        )
    return rows


def next_growth_tier(tradable_balance: float) -> dict:
    """Current tier production targets and the next milestone."""
    thresholds = sorted(TIER_LOT_STRUCTURES.keys())
    current_threshold = tier_threshold_for_equity(tradable_balance)
    current = capital_tier_detail(tradable_balance)
    idx = thresholds.index(current_threshold)
    if idx + 1 < len(thresholds):
        next_threshold = thresholds[idx + 1]
        nxt = capital_tier_detail(float(next_threshold))
        amount_to_next = max(round(next_threshold - tradable_balance, 2), 0.0)
    else:
        next_threshold = current_threshold
        nxt = current
        amount_to_next = 0.0
    return {
        "current_daily_target": current["daily_production_target"],
        "current_weekly_target": current["weekly_production_target"],
        "current_tier_balance": float(current_threshold),
        "current_tier_label": current["structure_label"],
        "current_lot_structure": current["lot_structure"],
        "next_balance": float(next_threshold),
        "next_daily_target": nxt["daily_production_target"],
        "next_weekly_target": nxt["weekly_production_target"],
        "amount_to_next_tier": amount_to_next,
        "weekly_opportunities": WEEKLY_PRODUCTION_OPPORTUNITIES,
        "milestone_daily_350_at": DAILY_TARGET_MILESTONE_AT,
    }
