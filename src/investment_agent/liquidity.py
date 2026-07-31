"""Liquidity cap and daily range metrics (Product Spec v3 / strategy doc §7)."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

# Strategy defaults
MIN_ADV_DOLLAR = 2_000_000.0
PARTICIPATION_RATE = 0.01
LIQUIDITY_BUFFER = 0.80
SWING_TARGET_PCT = 3.0
SWING_TOLERANCE_PCT = 1.0  # 2–4% band around 3%


@dataclass(frozen=True)
class DailyBar:
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class LiquidityMetrics:
    adv_dollar: float
    avg_range_pct: float
    liquidity_cap: float
    meets_liquidity_min: bool
    near_swing_target: bool


def daily_range_pct(bar: DailyBar) -> float:
    if bar.close <= 0:
        return 0.0
    return ((bar.high - bar.low) / bar.close) * 100.0


def compute_adv_dollar(bars: list[DailyBar], window: int = 20) -> float:
    if not bars:
        return 0.0
    recent = bars[-window:]
    dollars = [b.close * b.volume for b in recent if b.close > 0 and b.volume > 0]
    return mean(dollars) if dollars else 0.0


def compute_avg_range_pct(bars: list[DailyBar], window: int = 20) -> float:
    if not bars:
        return 0.0
    recent = bars[-window:]
    ranges = [daily_range_pct(b) for b in recent if b.close > 0]
    return mean(ranges) if ranges else 0.0


def liquidity_cap_from_adv(
    adv_dollar: float,
    participation_rate: float = PARTICIPATION_RATE,
    buffer: float = LIQUIDITY_BUFFER,
) -> float:
    return adv_dollar * participation_rate * buffer


def compute_liquidity_metrics(
    bars: list[DailyBar],
    tradable_cash: float | None = None,
    window: int = 20,
) -> LiquidityMetrics:
    adv = compute_adv_dollar(bars, window=window)
    avg_range = compute_avg_range_pct(bars, window=window)
    cap = liquidity_cap_from_adv(adv)
    if tradable_cash is not None:
        cap = min(cap, tradable_cash)
    meets_liq = adv >= MIN_ADV_DOLLAR
    near_swing = abs(avg_range - SWING_TARGET_PCT) <= SWING_TOLERANCE_PCT
    return LiquidityMetrics(
        adv_dollar=adv,
        avg_range_pct=avg_range,
        liquidity_cap=cap,
        meets_liquidity_min=meets_liq,
        near_swing_target=near_swing,
    )
