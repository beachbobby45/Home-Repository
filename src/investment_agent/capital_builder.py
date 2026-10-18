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

PHASE1_START = ORIGINAL_BASIS  # legacy $15k journal path
PHASE1_TARGET = 30_000.0
# Paper / staged RH funding band (Tony Oct 2026 plan)
PAPER_PHASE_START = 5_000.0
PAPER_PHASE_TARGET = 20_000.0
SOFT_TARGET_NOTE = (
    "Guidance only — up to 3 winning trades/week at tier net/trade; "
    "default is one #1 pick per day. A second trade only on exceptional days "
    "after #1 wins and market activity stays GO."
)


def _phase_bounds(conn: sqlite3.Connection | None) -> tuple[float, float]:
    if conn is None:
        return PHASE1_START, PHASE1_TARGET
    from investment_agent.execution.ops_audit import (
        LEDGER_SOURCE_PAPER,
        get_ledger_source,
    )

    if get_ledger_source(conn) == LEDGER_SOURCE_PAPER:
        return PAPER_PHASE_START, PAPER_PHASE_TARGET
    return PHASE1_START, PHASE1_TARGET


def phase1_journey_progress_pct(
    current_equity: float,
    *,
    start: float | None = None,
    target: float | None = None,
) -> float:
    """Percent complete along the phase path (0–100)."""
    lo = PHASE1_START if start is None else start
    hi = PHASE1_TARGET if target is None else target
    span = hi - lo
    if span <= 0:
        return 0.0
    return max(0.0, min(100.0, (current_equity - lo) / span * 100.0))


def phase1_of_target_pct(
    current_equity: float,
    *,
    target: float | None = None,
) -> float:
    """Current equity as percentage of the phase target."""
    hi = PHASE1_TARGET if target is None else target
    if hi <= 0:
        return 0.0
    return max(0.0, (current_equity / hi) * 100.0)


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
    phase_start, phase_target = _phase_bounds(conn)
    tier = capital_tier_detail(equity)
    weekly_target = tier["weekly_production_target"]
    weekly_net = snapshot.weekly_realized_net
    weekly_pct = round(weekly_production_progress_pct(weekly_net, weekly_target), 1)

    return CapitalBuilderProgress(
        phase1_start=phase_start,
        phase1_target=phase_target,
        current_equity=equity,
        tradable_cash=snapshot.tradable_cash,
        journey_progress_pct=round(
            phase1_journey_progress_pct(equity, start=phase_start, target=phase_target), 1
        ),
        of_target_pct=round(phase1_of_target_pct(equity, target=phase_target), 1),
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
        milestone_reached=equity >= phase_target,
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
    "PAPER_PHASE_START",
    "PAPER_PHASE_TARGET",
    "SOFT_TARGET_NOTE",
    "CapitalBuilderProgress",
    "build_capital_builder_progress",
    "phase1_journey_progress_pct",
    "phase1_of_target_pct",
    "progress_to_dict",
    "weekly_production_progress_pct",
    "weekly_production_target",
]
