"""Phase 1 Capital Builder milestone and weekly progress tracking."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from investment_agent.finance import (
    ORIGINAL_BASIS,
    capital_tier_detail,
    weekly_production_target,
)
from investment_agent.journal import today_pt_str
from investment_agent.risk_engine import build_portfolio_snapshot

PHASE1_START = ORIGINAL_BASIS
PHASE1_TARGET = 30_000.0
SOFT_TARGET_NOTE = (
    "Guidance only — 3 production opportunities per week at tier daily rate; "
    "no trade is required to hit the weekly band."
)


def phase1_journey_progress_pct(current_equity: float) -> float:
    """Percent complete along the $15K→$30K path (0–100)."""
    span = PHASE1_TARGET - PHASE1_START
    if span <= 0:
        return 0.0
    return max(0.0, min(100.0, (current_equity - PHASE1_START) / span * 100.0))


def phase1_of_target_pct(current_equity: float) -> float:
    """Current equity as percentage of the $30K Phase 1 target."""
    if PHASE1_TARGET <= 0:
        return 0.0
    return max(0.0, (current_equity / PHASE1_TARGET) * 100.0)


def weekly_production_progress_pct(weekly_net: float, weekly_target: float) -> float:
    """Weekly realized net as percent of tier weekly production guidance."""
    if weekly_target <= 0:
        return 0.0
    return (weekly_net / weekly_target) * 100.0


@dataclass(frozen=True)
class CapitalBuilderProgress:
    phase1_start: float
    phase1_target: float
    current_equity: float
    tradable_cash: float
    journey_progress_pct: float
    of_target_pct: float
    tier_threshold: float
    lot_structure: list[int]
    structure_label: str
    daily_production_target: float
    weekly_production_target: float
    weekly_opportunities: int
    weekly_realized_net: float
    weekly_production_progress_pct: float
    high_water_mark: float
    drawdown_pct: float
    kill_switch_active: bool
    milestone_reached: bool
    # API compatibility aliases
    weekly_soft_target: float
    weekly_soft_progress_pct: float


def build_capital_builder_progress(
    conn: sqlite3.Connection,
    *,
    date_key: str | None = None,
) -> CapitalBuilderProgress:
    when = date_key or today_pt_str()
    snapshot = build_portfolio_snapshot(conn, date_key=when)
    equity = snapshot.current_equity
    tier = capital_tier_detail(equity)
    weekly_target = tier["weekly_production_target"]
    weekly_net = snapshot.weekly_realized_net
    weekly_pct = round(weekly_production_progress_pct(weekly_net, weekly_target), 1)

    return CapitalBuilderProgress(
        phase1_start=PHASE1_START,
        phase1_target=PHASE1_TARGET,
        current_equity=equity,
        tradable_cash=snapshot.tradable_cash,
        journey_progress_pct=round(phase1_journey_progress_pct(equity), 1),
        of_target_pct=round(phase1_of_target_pct(equity), 1),
        tier_threshold=float(tier["tier_threshold"]),
        lot_structure=list(tier["lot_structure"]),
        structure_label=tier["structure_label"],
        daily_production_target=tier["daily_production_target"],
        weekly_production_target=weekly_target,
        weekly_opportunities=int(tier["weekly_opportunities"]),
        weekly_realized_net=weekly_net,
        weekly_production_progress_pct=weekly_pct,
        high_water_mark=snapshot.high_water_mark,
        drawdown_pct=snapshot.drawdown_pct,
        kill_switch_active=snapshot.kill_switch_active,
        milestone_reached=equity >= PHASE1_TARGET,
        weekly_soft_target=weekly_target,
        weekly_soft_progress_pct=weekly_pct,
    )


def progress_to_dict(progress: CapitalBuilderProgress) -> dict:
    return {
        "phase1_start": progress.phase1_start,
        "phase1_target": progress.phase1_target,
        "current_equity": progress.current_equity,
        "tradable_cash": progress.tradable_cash,
        "journey_progress_pct": progress.journey_progress_pct,
        "of_target_pct": progress.of_target_pct,
        "tier_threshold": progress.tier_threshold,
        "lot_structure": progress.lot_structure,
        "structure_label": progress.structure_label,
        "daily_production_target": progress.daily_production_target,
        "weekly_production_target": progress.weekly_production_target,
        "weekly_opportunities": progress.weekly_opportunities,
        "weekly_realized_net": progress.weekly_realized_net,
        "weekly_production_progress_pct": progress.weekly_production_progress_pct,
        "high_water_mark": progress.high_water_mark,
        "drawdown_pct": progress.drawdown_pct,
        "kill_switch_active": progress.kill_switch_active,
        "milestone_reached": progress.milestone_reached,
        "soft_target_note": SOFT_TARGET_NOTE,
        # Legacy API keys
        "weekly_soft_target": progress.weekly_soft_target,
        "weekly_soft_progress_pct": progress.weekly_soft_progress_pct,
    }


__all__ = [
    "PHASE1_START",
    "PHASE1_TARGET",
    "SOFT_TARGET_NOTE",
    "CapitalBuilderProgress",
    "build_capital_builder_progress",
    "phase1_journey_progress_pct",
    "phase1_of_target_pct",
    "progress_to_dict",
    "weekly_production_progress_pct",
    "weekly_production_target",
]
