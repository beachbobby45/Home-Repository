"""Strategy presets and scalable daily profit targets for backtesting."""

from __future__ import annotations

from dataclasses import dataclass

from investment_agent.finance import ORIGINAL_BASIS


def daily_profit_target(
    tradable_balance: float,
    *,
    base: float = 350.0,
    step: float = 50.0,
    every: float = 5_000.0,
    basis: float = ORIGINAL_BASIS,
) -> float:
    """
    Daily net profit goal scales +$50 for every $5K above $10K basis.
    $10K → $350, $15K → $400, $20K → $450, etc.
    """
    tiers = max(int((tradable_balance - basis) // every), 0)
    return base + tiers * step


def target_pct_for_dollars(
    *,
    net_needed: float,
    deploy_dollar: float,
    fees: float,
    min_pct: float = 1.0,
    max_pct: float = 4.0,
) -> float | None:
    """Percent move required on deploy_dollar to net net_needed after round-trip fees."""
    if deploy_dollar <= 0 or net_needed <= 0:
        return None
    gross_needed = net_needed + fees
    pct = 100.0 * gross_needed / deploy_dollar
    if pct < min_pct or pct > max_pct:
        return None
    return pct


@dataclass(frozen=True)
class StrategyModel:
    name: str
    description: str
    stop_pct: float
    max_trades_per_day: int
    entry_bar_delay: int  # 5m bars to skip after open (6 ≈ 30 min)
    stop_day_after_stop: bool
    target_pct: float | None = None  # fixed exit; None = dynamic dollar target
    daily_base_target: float = 350.0
    daily_step: float = 50.0
    daily_step_every: float = 5_000.0
    min_dynamic_target_pct: float = 1.0
    max_dynamic_target_pct: float = 4.0
    apply_monthly_sweeps: bool = True


RECOMMENDED_MODEL = StrategyModel(
    name="recommended",
    description="Wider stop, fewer trades, no re-entry after stop, 30m entry delay",
    target_pct=1.50,
    stop_pct=0.75,
    max_trades_per_day=2,
    entry_bar_delay=6,
    stop_day_after_stop=True,
    apply_monthly_sweeps=True,
)

DAILY_TARGET_MODEL = StrategyModel(
    name="daily_target_350",
    description="$350/day net (scales +$50 per $5K balance), dynamic per-trade target",
    target_pct=None,
    stop_pct=0.75,
    max_trades_per_day=3,
    entry_bar_delay=6,
    stop_day_after_stop=True,
    daily_base_target=350.0,
    apply_monthly_sweeps=True,
)

ORIGINAL_MODEL = StrategyModel(
    name="original",
    description="Original plan: +1.13% / −0.50%, unlimited re-entries",
    target_pct=1.13,
    stop_pct=0.50,
    max_trades_per_day=999,
    entry_bar_delay=0,
    stop_day_after_stop=False,
    apply_monthly_sweeps=False,
)

PRESETS: dict[str, StrategyModel] = {
    m.name: m for m in (ORIGINAL_MODEL, RECOMMENDED_MODEL, DAILY_TARGET_MODEL)
}
