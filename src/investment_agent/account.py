"""Account balance, jars, and dashboard summary (Product Spec v3)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.finance import (
    DAILY_TARGET_BASE,
    DAILY_TARGET_EVERY,
    DAILY_TARGET_MILESTONE_AT,
    DAILY_TARGET_MILESTONE_GOAL,
    DAILY_TARGET_STEP,
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    DEFAULT_SWEEP_SCHEDULE,
    DEFAULT_TAX_RESERVE_RATE,
    GOAL_ACCOUNT_VALUE,
    ORIGINAL_BASIS,
    SWEEP_SCHEDULE_ANNUAL,
    SWEEP_SCHEDULE_MONTHLY,
    VALID_SWEEP_SCHEDULES,
    compute_month_end_sweep,
    compute_period_end_sweep,
    daily_profit_target,
    goal_progress_pct,
    growth_plan_milestones,
    next_growth_tier,
    round_trip_fees,
)
from investment_agent.journal import (
    compute_monthly_realized_net,
    compute_today_realized_net,
    compute_total_fees,
    compute_ytd_realized_net,
    journal_cash_balance,
)
from investment_agent.strategy import (
    ENTRY_DELAY_MINUTES,
    ENTRY_WINDOW_ET,
    MAX_TRADES_PER_DAY,
    STOP_DAY_AFTER_STOP,
    STOP_PCT,
)

TRADING_MODE_KEY = "trading_mode"
TRADING_MODE_PAPER = "paper"
TRADING_MODE_LIVE = "live"
VALID_TRADING_MODES = frozenset({TRADING_MODE_PAPER, TRADING_MODE_LIVE})
SWEEP_SCHEDULE_KEY = "sweep_schedule"


@dataclass(frozen=True)
class DashboardSummary:
    tradable_cash: float
    original_basis: float
    goal_pct: float
    goal_target: float
    month_key: str
    period_key: str
    sweep_schedule: str
    monthly_realized_net: float
    period_realized_net: float
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
    daily_target: float
    today_realized_net: float
    today_target_progress_pct: float
    growth_tier: dict
    growth_plan: list[dict]
    strategy_rules: dict
    trading_mode: str


def _month_key(dt: datetime | None = None) -> str:
    when = dt or datetime.now(timezone.utc)
    return when.strftime("%Y-%m")


def _year_key(dt: datetime | None = None) -> str:
    when = dt or datetime.now(timezone.utc)
    return when.strftime("%Y")


def _annual_sweep_key(year_key: str | None = None) -> str:
    return f"{year_key or _year_key()}-annual"


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


def get_sweep_schedule(conn: sqlite3.Connection) -> str:
    raw = get_setting(conn, SWEEP_SCHEDULE_KEY, DEFAULT_SWEEP_SCHEDULE).lower().strip()
    return raw if raw in VALID_SWEEP_SCHEDULES else DEFAULT_SWEEP_SCHEDULE


def set_sweep_schedule(conn: sqlite3.Connection, schedule: str) -> str:
    normalized = schedule.lower().strip()
    if normalized not in VALID_SWEEP_SCHEDULES:
        raise ValueError(
            f"sweep_schedule must be one of: {', '.join(sorted(VALID_SWEEP_SCHEDULES))}"
        )
    set_setting(conn, SWEEP_SCHEDULE_KEY, normalized)
    return normalized


def get_trading_mode(conn: sqlite3.Connection) -> str:
    raw = get_setting(conn, TRADING_MODE_KEY, TRADING_MODE_PAPER).lower().strip()
    return raw if raw in VALID_TRADING_MODES else TRADING_MODE_PAPER


def set_trading_mode(conn: sqlite3.Connection, mode: str) -> str:
    normalized = mode.lower().strip()
    if normalized not in VALID_TRADING_MODES:
        raise ValueError(f"trading_mode must be one of: {', '.join(sorted(VALID_TRADING_MODES))}")
    set_setting(conn, TRADING_MODE_KEY, normalized)
    return normalized


def format_journal_notes(notes: str | None, mode: str) -> str | None:
    """Prefix journal notes with [PAPER] or [LIVE] unless already tagged."""
    prefix = "[PAPER]" if mode == TRADING_MODE_PAPER else "[LIVE]"
    if notes is None or not notes.strip():
        return prefix
    upper = notes.strip().upper()
    if upper.startswith("[PAPER]") or upper.startswith("[LIVE]"):
        return notes.strip()
    return f"{prefix} {notes.strip()}"


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


def sweep_applied_for_period(conn: sqlite3.Connection, period_key: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sweep_history WHERE month_key = ?", (period_key,)
    ).fetchone()
    return row is not None


def sweep_applied_for_month(conn: sqlite3.Connection, month_key: str) -> bool:
    return sweep_applied_for_period(conn, month_key)


def _record_sweep(
    conn: sqlite3.Connection,
    period_key: str,
    realized: float,
    sweep,
    tax_rate: float,
) -> dict:
    conn.execute(
        """
        INSERT INTO sweep_history
          (month_key, realized_net, management_amount, tax_amount, tax_rate)
        VALUES (?, ?, ?, ?, ?)
        """,
        (period_key, realized, sweep.management_sweep, sweep.tax_sweep, tax_rate),
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
        "period_key": period_key,
        "month_key": period_key,
        "realized_net": realized,
        "management_sweep": sweep.management_sweep,
        "tax_sweep": sweep.tax_sweep,
        "total_sweep": sweep.total_sweep,
        "sweep_schedule": get_sweep_schedule(conn),
    }


def apply_month_end_sweep(conn: sqlite3.Connection, month_key: str | None = None) -> dict:
    """Record month-end sweep into jars (idempotent per month)."""
    mk = month_key or _month_key()
    if sweep_applied_for_period(conn, mk):
        return {"ok": False, "error": f"Sweep already applied for {mk}"}

    tax_rate = get_tax_rate(conn)
    realized = compute_monthly_realized_net(conn, mk)
    sweep = compute_period_end_sweep(realized, tax_rate=tax_rate)
    if not sweep.applies:
        return {
            "ok": False,
            "error": f"No positive realized net for {mk} (${realized:.2f})",
        }
    return _record_sweep(conn, mk, realized, sweep, tax_rate)


def apply_annual_sweep(conn: sqlite3.Connection, year_key: str | None = None) -> dict:
    """Record year-end sweep on YTD realized net (idempotent per year)."""
    yk = year_key or _year_key()
    period_key = _annual_sweep_key(yk)
    if sweep_applied_for_period(conn, period_key):
        return {"ok": False, "error": f"Sweep already applied for {yk}"}

    tax_rate = get_tax_rate(conn)
    realized = compute_ytd_realized_net(conn, yk)
    sweep = compute_period_end_sweep(realized, tax_rate=tax_rate)
    if not sweep.applies:
        return {
            "ok": False,
            "error": f"No positive YTD realized net for {yk} (${realized:.2f})",
        }
    return _record_sweep(conn, period_key, realized, sweep, tax_rate)


def apply_period_sweep(conn: sqlite3.Connection) -> dict:
    """Apply sweep using configured schedule (annual default, or monthly)."""
    schedule = get_sweep_schedule(conn)
    if schedule == SWEEP_SCHEDULE_ANNUAL:
        return apply_annual_sweep(conn)
    return apply_month_end_sweep(conn)


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
    yk = _year_key()
    tax_rate = get_tax_rate(conn)
    schedule = get_sweep_schedule(conn)
    period_key = _annual_sweep_key(yk) if schedule == SWEEP_SCHEDULE_ANNUAL else mk
    journal_cash = journal_cash_balance(conn)
    sweeps = cumulative_sweeps(conn)
    tradable = journal_cash - sweeps
    monthly_realized = compute_monthly_realized_net(conn, mk)
    period_realized = (
        compute_ytd_realized_net(conn, yk)
        if schedule == SWEEP_SCHEDULE_ANNUAL
        else monthly_realized
    )
    sweep = compute_period_end_sweep(period_realized, tax_rate=tax_rate)
    vix = latest_vix(conn)
    regime = latest_regime(conn)
    daily_target = daily_profit_target(tradable)
    today_net = compute_today_realized_net(conn)
    today_progress = (today_net / daily_target * 100.0) if daily_target > 0 else 0.0

    return DashboardSummary(
        tradable_cash=tradable,
        original_basis=ORIGINAL_BASIS,
        goal_pct=goal_progress_pct(tradable),
        goal_target=GOAL_ACCOUNT_VALUE,
        month_key=mk,
        period_key=period_key,
        sweep_schedule=schedule,
        monthly_realized_net=monthly_realized,
        period_realized_net=period_realized,
        total_fees_paid=compute_total_fees(conn),
        sweep_preview={
            "applies": sweep.applies,
            "management_sweep": sweep.management_sweep,
            "tax_sweep": sweep.tax_sweep,
            "total_sweep": sweep.total_sweep,
            "monthly_realized_net": monthly_realized,
            "period_realized_net": period_realized,
            "period_label": "YTD" if schedule == SWEEP_SCHEDULE_ANNUAL else "month",
        },
        management_jar=get_jar_balance(conn, "management"),
        tax_jar=get_jar_balance(conn, "tax"),
        tax_rate=tax_rate,
        sweep_already_applied=sweep_applied_for_period(conn, period_key),
        vix=vix,
        regime=regime,
        market_brief=build_market_brief(vix, regime),
        block_new_longs=bool(regime and regime.get("block_new_longs")),
        daily_target=daily_target,
        today_realized_net=today_net,
        today_target_progress_pct=today_progress,
        growth_tier=next_growth_tier(tradable),
        growth_plan=growth_plan_milestones(),
        strategy_rules={
            "daily_net_target": daily_target,
            "stop_pct": STOP_PCT,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "entry_window_et": ENTRY_WINDOW_ET,
            "stop_day_after_stop": STOP_DAY_AFTER_STOP,
            "daily_target_base": DAILY_TARGET_BASE,
            "daily_target_step": DAILY_TARGET_STEP,
            "daily_target_every": DAILY_TARGET_EVERY,
            "milestone_daily_goal": DAILY_TARGET_MILESTONE_GOAL,
            "milestone_at_balance": DAILY_TARGET_MILESTONE_AT,
        },
        trading_mode=get_trading_mode(conn),
    )


def summary_to_dict(summary: DashboardSummary) -> dict:
    return {
        "tradable_cash": summary.tradable_cash,
        "original_basis": summary.original_basis,
        "goal_pct": summary.goal_pct,
        "goal_target": summary.goal_target,
        "month_key": summary.month_key,
        "period_key": summary.period_key,
        "sweep_schedule": summary.sweep_schedule,
        "monthly_realized_net": summary.monthly_realized_net,
        "period_realized_net": summary.period_realized_net,
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
        "daily_target": summary.daily_target,
        "today_realized_net": summary.today_realized_net,
        "today_target_progress_pct": summary.today_target_progress_pct,
        "growth_tier": summary.growth_tier,
        "growth_plan": summary.growth_plan,
        "strategy": summary.strategy_rules,
        "trading_mode": summary.trading_mode,
    }
