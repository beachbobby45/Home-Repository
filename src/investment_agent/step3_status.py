"""Step 3 eligibility labels for watchlist / Special Watch reporting."""

from __future__ import annotations

from investment_agent.liquidity import SWING_TARGET_PCT, SWING_TOLERANCE_PCT

STEP3_PASS = "step3_pass"
TOO_QUIET = "too_quiet"
TOO_WILD = "too_wild"
LOW_LIQUIDITY = "low_liquidity"
MISSING_METRICS = "missing_metrics"
REGIME_ONLY = "regime_only"

STEP3_STATUS_LABELS: dict[str, str] = {
    STEP3_PASS: "Step 3 pass",
    TOO_QUIET: "Too quiet",
    TOO_WILD: "Too wild",
    LOW_LIQUIDITY: "Low liquidity",
    MISSING_METRICS: "Missing metrics",
    REGIME_ONLY: "Regime only",
}


def swing_band_low() -> float:
    return SWING_TARGET_PCT - SWING_TOLERANCE_PCT


def swing_band_high() -> float:
    return SWING_TARGET_PCT + SWING_TOLERANCE_PCT


def classify_step3_status(
    *,
    ticker: str = "",
    meets_liquidity: bool | None = None,
    near_swing: bool | None = None,
    avg_range_pct: float | None = None,
    regime_only: bool = False,
) -> str:
    if regime_only:
        return REGIME_ONLY
    if meets_liquidity is None and avg_range_pct is None:
        return MISSING_METRICS
    if meets_liquidity is False:
        return LOW_LIQUIDITY
    if near_swing:
        return STEP3_PASS
    if avg_range_pct is not None:
        if avg_range_pct < swing_band_low():
            return TOO_QUIET
        if avg_range_pct > swing_band_high():
            return TOO_WILD
    return TOO_QUIET
