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
