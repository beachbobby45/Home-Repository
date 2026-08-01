"""Account balance, jars, and dashboard summary (Product Spec v3)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    DEFAULT_TAX_RESERVE_RATE,
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    goal_progress_pct,
    round_trip_fees,
)
from investment_agent.journal import (
    compute_monthly_realized_net,
    compute_total_fees,
    journal_cash_balance,
)


@dataclass(frozen=True)
class DashboardSummary:
    tradable_cash: float
    original_basis: float
    goal_pct: float
    goal_target: float
    month_key: str
    monthly_realized_net: float
    total_fees_paid: float
    sweep_preview: dict
    management_jar: float
    tax_jar: float
    tax_rate: float
    sweep_already_applied: bool
    vix: float | None
    regime: dict | None
    market_brief: str
    block_new_longs: bool


def _month_key(dt: datetime | None = None) -> str:
    when = dt or datetime.now(timezone.utc)
    return when.strftime("%Y-%m")


def get_setting(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute(
        "SELECT value FROM app_settings WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET
          value = excluded.value,
          updated_at = excluded.updated_at
        """,
        (key, value),
    )


def get_tax_rate(conn: sqlite3.Connection) -> float:
    raw = get_setting(conn, "tax_reserve_rate", str(DEFAULT_TAX_RESERVE_RATE))
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_TAX_RESERVE_RATE


def get_jar_balance(conn: sqlite3.Connection, jar_type: str) -> float:
    row = conn.execute(
        "SELECT balance FROM jar_balances WHERE jar_type = ?", (jar_type,)
    ).fetchone()
    return float(row["balance"]) if row else 0.0


def cumulative_sweeps(conn: sqlite3.Connection) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS total FROM sweep_history"
    ).fetchone()
    return float(row["total"]) if row else 0.0


def sweep_applied_for_month(conn: sqlite3.Connection, month_key: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sweep_history WHERE month_key = ?", (month_key,)
    ).fetchone()
    return row is not None


def apply_month_end_sweep(conn: sqlite3.Connection, month_key: str | None = None) -> dict:
    """Record month-end sweep into jars (idempotent per month)."""
    mk = month_key or _month_key()
    if sweep_applied_for_month(conn, mk):
        return {"ok": False, "error": f"Sweep already applied for {mk}"}

    tax_rate = get_tax_rate(conn)
    realized = compute_monthly_realized_net(conn, mk)
    sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
    if not sweep.applies:
        return {
            "ok": False,
            "error": f"No positive realized net for {mk} (${realized:.2f})",
        }

    conn.execute(
        """
        INSERT INTO sweep_history
          (month_key, realized_net, management_amount, tax_amount, tax_rate)
        VALUES (?, ?, ?, ?, ?)
        """,
        (mk, realized, sweep.management_sweep, sweep.tax_sweep, tax_rate),
    )
    for jar_type, amount in (
        ("management", sweep.management_sweep),
        ("tax", sweep.tax_sweep),
    ):
        conn.execute(
            """
            INSERT INTO jar_balances (jar_type, balance, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(jar_type) DO UPDATE SET
              balance = balance + excluded.balance,
              updated_at = datetime('now')
            """,
            (jar_type, amount),
        )
    return {
        "ok": True,
        "month_key": mk,
        "realized_net": realized,
        "management_sweep": sweep.management_sweep,
        "tax_sweep": sweep.tax_sweep,
        "total_sweep": sweep.total_sweep,
    }


def latest_vix(conn: sqlite3.Connection) -> float | None:
    row = conn.execute(
        """
        SELECT value FROM macro_snapshots
        WHERE series_id = 'VIXCLS'
        ORDER BY observation_date DESC
        LIMIT 1
        """
    ).fetchone()
    return float(row["value"]) if row else None


def latest_regime(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        """
        SELECT captured_at, spy_change_pct, dia_change_pct, qqq_change_pct,
               block_new_longs, summary
        FROM regime_snapshots
        ORDER BY captured_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return None
    return {
        "captured_at": row["captured_at"],
        "spy_change_pct": row["spy_change_pct"],
        "dia_change_pct": row["dia_change_pct"],
        "qqq_change_pct": row["qqq_change_pct"],
        "block_new_longs": bool(row["block_new_longs"]),
        "summary": row["summary"],
    }


def build_market_brief(vix: float | None, regime: dict | None) -> str:
    parts: list[str] = []
    if vix is not None:
        tone = "elevated" if vix >= 20 else "moderate" if vix >= 15 else "calm"
        parts.append(f"VIX {vix:.2f} ({tone}).")
    if regime:
        parts.append(regime["summary"])
    else:
        parts.append("Run ingest to refresh regime data.")
    parts.append(
        "Rule-based brief (no Claude). Add Anthropic credits later for CIO narratives."
    )
    return " ".join(parts)


def build_dashboard_summary(conn: sqlite3.Connection) -> DashboardSummary:
    mk = _month_key()
    tax_rate = get_tax_rate(conn)
    journal_cash = journal_cash_balance(conn)
    sweeps = cumulative_sweeps(conn)
    tradable = journal_cash - sweeps
    realized = compute_monthly_realized_net(conn, mk)
    sweep = compute_month_end_sweep(realized, tax_rate=tax_rate)
    vix = latest_vix(conn)
    regime = latest_regime(conn)

    return DashboardSummary(
        tradable_cash=tradable,
        original_basis=ORIGINAL_BASIS,
        goal_pct=goal_progress_pct(tradable),
        goal_target=GOAL_ACCOUNT_VALUE,
        month_key=mk,
        monthly_realized_net=realized,
        total_fees_paid=compute_total_fees(conn),
        sweep_preview={
            "applies": sweep.applies,
            "management_sweep": sweep.management_sweep,
            "tax_sweep": sweep.tax_sweep,
            "total_sweep": sweep.total_sweep,
            "monthly_realized_net": realized,
        },
        management_jar=get_jar_balance(conn, "management"),
        tax_jar=get_jar_balance(conn, "tax"),
        tax_rate=tax_rate,
        sweep_already_applied=sweep_applied_for_month(conn, mk),
        vix=vix,
        regime=regime,
        market_brief=build_market_brief(vix, regime),
        block_new_longs=bool(regime and regime.get("block_new_longs")),
    )


def summary_to_dict(summary: DashboardSummary) -> dict:
    return {
        "tradable_cash": summary.tradable_cash,
        "original_basis": summary.original_basis,
        "goal_pct": summary.goal_pct,
        "goal_target": summary.goal_target,
        "month_key": summary.month_key,
        "monthly_realized_net": summary.monthly_realized_net,
        "total_fees_paid": summary.total_fees_paid,
        "round_trip_fee": round_trip_fees(DEFAULT_BUY_FEE, DEFAULT_SELL_FEE),
        "sweep_preview": summary.sweep_preview,
        "management_jar": summary.management_jar,
        "tax_jar": summary.tax_jar,
        "tax_rate": summary.tax_rate,
        "sweep_already_applied": summary.sweep_already_applied,
        "vix": summary.vix,
        "regime": summary.regime,
        "market_brief": summary.market_brief,
        "block_new_longs": summary.block_new_longs,
    }
