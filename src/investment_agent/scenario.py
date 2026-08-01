"""$5M goal scenario visualizer — journal-fed actuals + projections (Phase 6)."""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.account import get_tax_rate
from investment_agent.finance import (
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    goal_progress_pct,
)
from investment_agent.journal import compute_monthly_realized_net

MAX_PROJECTION_MONTHS = 360
DEFAULT_PROJECTION_HORIZON = 120


@dataclass(frozen=True)
class TimelinePoint:
    month_key: str
    tradable_balance: float
    goal_pct: float
    monthly_realized_net: float
    sweep_total: float
    fees_in_month: float
    label: str


def _month_keys_from_journal(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT strftime('%Y-%m', executed_at) AS mk
        FROM trade_journal
        ORDER BY mk ASC
        """
    ).fetchall()
    return [row["mk"] for row in rows]


def _journal_cash_through(conn: sqlite3.Connection, month_key: str) -> float:
    cash = ORIGINAL_BASIS
    rows = conn.execute(
        """
        SELECT side, shares, price, fee
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) <= ?
        ORDER BY executed_at ASC, id ASC
        """,
        (month_key,),
    ).fetchall()
    for row in rows:
        notional = row["shares"] * row["price"]
        if row["side"] == "BUY":
            cash -= notional + row["fee"]
        else:
            cash += notional - row["fee"]
    return cash


def _fees_in_month(conn: sqlite3.Connection, month_key: str) -> float:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(fee), 0) AS total
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) = ?
        """,
        (month_key,),
    ).fetchone()
    return float(row["total"]) if row else 0.0


def _cumulative_sweeps_through(
    conn: sqlite3.Connection,
    through_month: str,
    tax_rate: float,
    months: list[str],
) -> float:
    total = 0.0
    for mk in months:
        if mk > through_month:
            break
        realized = compute_monthly_realized_net(conn, mk)
        sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
        total += sweep.total_sweep
    return total


def replay_actual_timeline(conn: sqlite3.Connection) -> list[TimelinePoint]:
    """Month-by-month tradable balance from journal + computed month-end sweeps."""
    tax_rate = get_tax_rate(conn)
    months = _month_keys_from_journal(conn)
    points: list[TimelinePoint] = [
        TimelinePoint(
            month_key="start",
            tradable_balance=ORIGINAL_BASIS,
            goal_pct=goal_progress_pct(ORIGINAL_BASIS),
            monthly_realized_net=0.0,
            sweep_total=0.0,
            fees_in_month=0.0,
            label="Start ($10K basis)",
        )
    ]

    for mk in months:
        cash = _journal_cash_through(conn, mk)
        sweeps = _cumulative_sweeps_through(conn, mk, tax_rate, months)
        tradable = cash - sweeps
        realized = compute_monthly_realized_net(conn, mk)
        sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
        points.append(
            TimelinePoint(
                month_key=mk,
                tradable_balance=tradable,
                goal_pct=goal_progress_pct(tradable),
                monthly_realized_net=realized,
                sweep_total=sweep.total_sweep,
                fees_in_month=_fees_in_month(conn, mk),
                label=mk,
            )
        )
    return points


def _tradable_at_month_end(
    conn: sqlite3.Connection,
    month_key: str,
    months: list[str],
    tax_rate: float,
) -> float:
    cash = _journal_cash_through(conn, month_key)
    sweeps = _cumulative_sweeps_through(conn, month_key, tax_rate, months)
    return cash - sweeps


def _journal_pace_monthly_return(
    conn: sqlite3.Connection,
    months: list[str],
    tax_rate: float,
) -> float | None:
    """
    Average monthly return from realized P&L / tradable balance at month start.
    Avoids distortion when cash moves into open positions mid-month.
    """
    if not months:
        return None
    returns: list[float] = []
    prior_tradable = ORIGINAL_BASIS
    for mk in months:
        realized = compute_monthly_realized_net(conn, mk)
        if prior_tradable > 0:
            returns.append(realized / prior_tradable)
        prior_tradable = _tradable_at_month_end(conn, mk, months, tax_rate)
    if not returns:
        return None
    if all(r <= 0 for r in returns):
        return None
    geo = 1.0
    for r in returns:
        geo *= max(1.0 + r, 0.001)
    return geo ** (1.0 / len(returns)) - 1.0


def _avg_monthly_return_pct(
    conn: sqlite3.Connection,
    months: list[str],
    tax_rate: float,
) -> float | None:
    return _journal_pace_monthly_return(conn, months, tax_rate)


def _months_to_goal(balance: float, goal: float, monthly_return: float) -> float | None:
    if balance <= 0 or goal <= balance:
        return 0.0 if goal <= balance else None
    if monthly_return <= 0:
        return None
    growth = 1.0 + monthly_return
    if growth <= 1.0:
        return None
    return math.log(goal / balance) / math.log(growth)


def _project_balance(
    start_balance: float,
    monthly_return: float,
    months: int,
) -> list[dict]:
    pts: list[dict] = []
    bal = start_balance
    for offset in range(months + 1):
        pts.append(
            {
                "month_offset": offset,
                "balance": bal,
                "goal_pct": goal_progress_pct(bal),
            }
        )
        bal *= 1.0 + monthly_return
    return pts


def build_scenario_visualizer(
    conn: sqlite3.Connection,
    *,
    projection_horizon: int = DEFAULT_PROJECTION_HORIZON,
) -> dict:
    horizon = min(max(projection_horizon, 12), MAX_PROJECTION_MONTHS)
    actual = replay_actual_timeline(conn)
    current = actual[-1] if actual else None
    current_balance = current.tradable_balance if current else ORIGINAL_BASIS
    current_goal_pct = current.goal_pct if current else goal_progress_pct(ORIGINAL_BASIS)

    tax_rate = get_tax_rate(conn)
    month_list = _month_keys_from_journal(conn)
    avg_return = _avg_monthly_return_pct(conn, month_list, tax_rate)
    journal_months = [p for p in actual if p.month_key != "start"]

    # Include mark-to-market for open positions in current account value
    from investment_agent.journal import get_open_positions
    from investment_agent.monitor import get_latest_quotes

    quotes = get_latest_quotes(conn)
    account_value = current_balance
    for pos in get_open_positions(conn):
        px = quotes.get(pos["ticker"], pos["avg_cost"])
        account_value += pos["shares"] * px

    scenarios: dict[str, dict] = {}

    # Journal pace — compound at observed avg monthly return
    if avg_return is not None and avg_return > 0:
        months_to = _months_to_goal(account_value, GOAL_ACCOUNT_VALUE, avg_return)
        scenarios["journal_pace"] = {
            "name": "Journal pace",
            "description": (
                f"Compound at {avg_return * 100:.2f}% avg monthly realized return "
                f"from {len(journal_months)} logged month(s)."
            ),
            "monthly_return_pct": avg_return * 100,
            "months_to_goal": months_to,
            "reachable": months_to is not None and months_to <= horizon * 2,
            "points": _project_balance(account_value, avg_return, horizon),
        }
    else:
        scenarios["journal_pace"] = {
            "name": "Journal pace",
            "description": "Not enough positive journal history to project (need 2+ months with gains).",
            "monthly_return_pct": (avg_return or 0) * 100,
            "months_to_goal": None,
            "reachable": False,
            "points": _project_balance(account_value, 0.0, min(horizon, 24)),
        }

    # Strategy reference — uses account value including open positions
    trades_per_month = 0.0
    if journal_months:
        round_trips = sum(
            1
            for p in journal_months
            if p.monthly_realized_net != 0
        ) or len(journal_months)
        trades_per_month = max(round_trips, 1.0)
    # ~3-4 trades/day * ~16 days = ~56 trades/mo is max cadence; scale from journal
    strategy_monthly = (1.013**max(trades_per_month, 4)) - 1.0 if trades_per_month else 0.013
    strategy_monthly = min(strategy_monthly, 0.50)  # cap unrealistic projection
    scenarios["strategy_reference"] = {
        "name": "Strategy reference",
        "description": (
            f"If ~{max(int(trades_per_month), 4)} round trips/month at +1.13% target "
            f"(fees not modeled in projection)."
        ),
        "monthly_return_pct": strategy_monthly * 100,
        "months_to_goal": _months_to_goal(account_value, GOAL_ACCOUNT_VALUE, strategy_monthly),
        "reachable": True,
        "points": _project_balance(account_value, strategy_monthly, horizon),
    }

    # Required return to hit $5M in 10 years (120 months)
    required_10y = None
    if account_value > 0 and account_value < GOAL_ACCOUNT_VALUE:
        g = (GOAL_ACCOUNT_VALUE / account_value) ** (1.0 / 120) - 1.0
        required_10y = g
    scenarios["required_10yr"] = {
        "name": "Required (10 yr)",
        "description": "Monthly return needed to reach $5M in 120 months from today.",
        "monthly_return_pct": (required_10y or 0) * 100,
        "months_to_goal": 120.0 if required_10y else None,
        "reachable": required_10y is not None,
        "points": _project_balance(account_value, required_10y or 0, 120) if required_10y else [],
    }

    total_realized = sum(p.monthly_realized_net for p in journal_months)
    total_fees = sum(p.fees_in_month for p in journal_months)
    total_sweeps = sum(p.sweep_total for p in journal_months)

    summary_parts = [
        f"Tradable cash ${current_balance:,.2f}; account value ${account_value:,.2f} "
        f"({goal_progress_pct(account_value):.4f}% of $5M incl. open positions).",
        f"Journal spans {len(journal_months)} month(s); "
        f"realized net ${total_realized:+,.2f}, fees ${total_fees:,.2f}, sweeps ${total_sweeps:,.2f}.",
    ]
    jp = scenarios["journal_pace"]
    if jp.get("months_to_goal"):
        summary_parts.append(
            f"At journal pace ({jp['monthly_return_pct']:.2f}%/mo), "
            f"~{jp['months_to_goal']:.0f} months to $5M."
        )
    else:
        summary_parts.append("Journal pace cannot reach $5M — improve edge or cadence.")

    return {
        "goal": GOAL_ACCOUNT_VALUE,
        "original_basis": ORIGINAL_BASIS,
        "current_balance": current_balance,
        "account_value": account_value,
        "current_goal_pct": goal_progress_pct(account_value),
        "actual_timeline": [_point_to_dict(p) for p in actual],
        "scenarios": scenarios,
        "summary": " ".join(summary_parts),
        "projection_horizon_months": horizon,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def _point_to_dict(p: TimelinePoint) -> dict:
    return {
        "month_key": p.month_key,
        "tradable_balance": p.tradable_balance,
        "goal_pct": p.goal_pct,
        "monthly_realized_net": p.monthly_realized_net,
        "sweep_total": p.sweep_total,
        "fees_in_month": p.fees_in_month,
        "label": p.label,
    }
