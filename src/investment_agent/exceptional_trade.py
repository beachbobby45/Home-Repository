"""Exceptional trade override — max 1 extra opportunity/week (Phase 1B Inc 17).

When weekly production guidance is met, default stop applies. One additional
trade per week is allowed only when Market Activity is Exceptional, confirmation
PASSes on the pick, and risk approves.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from investment_agent.journal import _week_start_pt, today_pt_str

MAX_EXCEPTIONAL_TRADES_PER_WEEK = 1


def count_exceptional_trades_consumed(
    conn: sqlite3.Connection,
    *,
    date_key: str | None = None,
) -> int:
    """How many exceptional slots were used this ISO week (Pacific)."""
    when = date_key or today_pt_str()
    week_start = _week_start_pt(when)
    row = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM exceptional_trade_log
        WHERE week_start_pt = ? AND consumed_at IS NOT NULL
        """,
        (week_start,),
    ).fetchone()
    return int(row["c"]) if row else 0


def evaluate_exceptional_trade(
    *,
    weekly_target_met: bool,
    market_activity: dict,
    confirmations: list[dict],
    pick_ticker: str | None,
    phase: str,
    stopped: bool,
    open_positions_count: int,
    portfolio_risk_verdict: str,
    exceptional_consumed_this_week: int,
) -> dict:
    """Return eligibility and whether the override is active for new entries."""
    slot_available = exceptional_consumed_this_week < MAX_EXCEPTIONAL_TRADES_PER_WEEK
    band = market_activity.get("band")
    ma_ok = bool(market_activity.get("allow_trade")) and band == "exceptional"

    pick_conf = None
    if pick_ticker:
        pick_conf = next(
            (c for c in confirmations if c.get("ticker") == pick_ticker.upper()),
            None,
        )
    confirmation_ok = bool(pick_conf and pick_conf.get("passes"))

    base_checks = [
        ("Weekly guidance met", weekly_target_met),
        ("Exceptional slot available", slot_available),
        ("Exceptional market day", ma_ok),
        ("Confirmation PASS on pick", confirmation_ok),
        ("Trade window", phase == "trade_window"),
        ("No stop-out today", not stopped),
        ("Room for entry", open_positions_count < 2),
        ("Risk approved", portfolio_risk_verdict == "approved"),
    ]
    checks = [{"name": name, "ok": ok} for name, ok in base_checks]
    all_go = all(ok for _, ok in base_checks)

    active = weekly_target_met and all_go
    eligible = weekly_target_met and slot_available and ma_ok and confirmation_ok

    if active:
        summary = (
            f"Exceptional override — 1 extra trade allowed this week "
            f"({pick_ticker} confirms on Exceptional day)"
        )
    elif weekly_target_met and not slot_available:
        summary = "Weekly guidance met — exceptional slot already used this week"
    elif weekly_target_met:
        summary = "Weekly guidance met — default stop (exceptional signals not all GO)"
    else:
        summary = "Weekly guidance not yet met"

    return {
        "active": active,
        "eligible": eligible,
        "slot_available": slot_available,
        "consumed_this_week": exceptional_consumed_this_week,
        "max_per_week": MAX_EXCEPTIONAL_TRADES_PER_WEEK,
        "checks": checks,
        "summary": summary,
        "pick_ticker": pick_ticker,
        "market_activity_band": band,
        "confirmation_score": pick_conf.get("score") if pick_conf else None,
    }


def log_exceptional_trade_consumed(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    ticker: str,
    journal_buy_id: int,
    market_activity: dict,
    confirmation_score: int | None,
    notes: str | None = None,
) -> None:
    """Record that the weekly exceptional slot was used."""
    week_start = _week_start_pt(today_pt_str())
    consumed = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn.execute(
        """
        INSERT INTO exceptional_trade_log
          (week_start_pt, session_date_et, ticker, journal_buy_id, consumed_at,
           market_activity_score, market_activity_band, confirmation_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            week_start,
            session_date_et,
            ticker.upper(),
            journal_buy_id,
            consumed,
            market_activity.get("score"),
            market_activity.get("band"),
            confirmation_score,
            notes,
        ),
    )


def exceptional_trade_to_dict(result: dict) -> dict:
    return {
        "active": result.get("active", False),
        "eligible": result.get("eligible", False),
        "slot_available": result.get("slot_available", True),
        "consumed_this_week": result.get("consumed_this_week", 0),
        "max_per_week": result.get("max_per_week", MAX_EXCEPTIONAL_TRADES_PER_WEEK),
        "checks": result.get("checks") or [],
        "summary": result.get("summary"),
        "pick_ticker": result.get("pick_ticker"),
        "market_activity_band": result.get("market_activity_band"),
        "confirmation_score": result.get("confirmation_score"),
    }
