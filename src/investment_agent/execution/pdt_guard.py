"""Day-trade frequency guard (post–PDT regulatory regime).

FINRA replaced Pattern Day Trader rules with intraday margin standards
effective 2026-06-04 (Regulatory Notice 26-10). Robinhood removed day-trade
count restrictions the same day.

Operator policy (2026-10-18):
  - Max **5** filled day trades per calendar week (one per weekday).
  - No $25k / 3-trade regulatory split.
  - Settled-cash checks live elsewhere (broker sync); this module only
    tracks filled same-day round-trips for the ops cap.

A day trade = buy and sell of the same symbol on the same session date.
No-fill / cancelled entry does not consume a slot.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

# Legacy name kept for import compatibility; threshold no longer changes the cap.
PDT_EQUITY_THRESHOLD = 25_000.0
MAX_DAY_TRADES_PER_WEEK = 5
# Back-compat aliases
MAX_DAY_TRADES_BELOW_25K = MAX_DAY_TRADES_PER_WEEK
MAX_DAY_TRADES_AT_OR_ABOVE_25K = MAX_DAY_TRADES_PER_WEEK


def max_day_trades_per_week(equity: float | None = None) -> int:
    """Return weekly day-trade ops cap (always 5 under current policy)."""
    _ = equity  # retained for call-site compatibility
    return MAX_DAY_TRADES_PER_WEEK


def week_monday_et(session_date: date | str) -> date:
    """ISO-style week key: Monday of the calendar week containing ``session_date`` (ET)."""
    if isinstance(session_date, str):
        d = date.fromisoformat(session_date[:10])
    else:
        d = session_date
    return d - timedelta(days=d.weekday())


def _today_et() -> date:
    return datetime.now(ET).date()


def count_day_trades_in_week(
    conn: sqlite3.Connection,
    session_date: date | str,
    *,
    week_start: date | None = None,
) -> int:
    """Count recorded day trades in the calendar week of ``session_date``."""
    start = week_start or week_monday_et(session_date)
    end = start + timedelta(days=6)
    row = conn.execute(
        """
        SELECT COUNT(*) AS n FROM pdt_day_trades
        WHERE session_date_et >= ? AND session_date_et <= ?
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return int(row["n"] if row else 0)


def can_open_day_trade(
    conn: sqlite3.Connection,
    *,
    equity: float,
    session_date: date | str | None = None,
) -> dict:
    """Whether another same-day round-trip is allowed this week (ops cap)."""
    day = session_date or _today_et()
    if isinstance(day, str):
        day_s = day[:10]
        day_d = date.fromisoformat(day_s)
    else:
        day_s = day.isoformat()
        day_d = day

    cap = max_day_trades_per_week(equity)
    week_start = week_monday_et(day_d)
    used = count_day_trades_in_week(conn, day_d, week_start=week_start)
    remaining = max(cap - used, 0)
    allowed = used < cap

    existing = conn.execute(
        "SELECT id FROM pdt_day_trades WHERE session_date_et = ?",
        (day_s,),
    ).fetchone()

    return {
        "allowed": allowed and existing is None,
        "reason": (
            None
            if allowed and existing is None
            else (
                "day_trade_already_recorded_for_session"
                if existing is not None
                else f"weekly_cap_reached_{cap}"
            )
        ),
        "equity": float(equity),
        "cap": cap,
        "used": used,
        "remaining": remaining if existing is None else remaining,
        "week_start_et": week_start.isoformat(),
        "session_date_et": day_s,
        "already_recorded_today": existing is not None,
        "regulatory_note": (
            "Post-PDT ops cap (max 5/week). FINRA/RH no longer enforce "
            "3-under-$25k trade counts as of 2026-06-04."
        ),
    }


def record_day_trade(
    conn: sqlite3.Connection,
    *,
    session_date: date | str,
    ticker: str,
    equity_at_trade: float,
    broker_fill_id: str | None = None,
    notes: str | None = None,
) -> int:
    """Persist a completed day trade (call only after buy+sell same session)."""
    if isinstance(session_date, str):
        day_s = session_date[:10]
        day_d = date.fromisoformat(day_s)
    else:
        day_s = session_date.isoformat()
        day_d = session_date

    gate = can_open_day_trade(conn, equity=equity_at_trade, session_date=day_d)
    if gate["already_recorded_today"]:
        raise ValueError(f"Day trade already recorded for {day_s}")
    if gate["used"] >= gate["cap"]:
        raise ValueError(
            f"Weekly day-trade cap {gate['cap']} already reached "
            f"(week {gate['week_start_et']})"
        )

    now = datetime.now(ET).replace(microsecond=0).isoformat()
    cur = conn.execute(
        """
        INSERT INTO pdt_day_trades
          (session_date_et, week_start_et, ticker, equity_at_trade, cap_at_trade,
           broker_fill_id, notes, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            day_s,
            week_monday_et(day_d).isoformat(),
            ticker.upper(),
            float(equity_at_trade),
            int(gate["cap"]),
            broker_fill_id,
            notes,
            now,
        ),
    )
    return int(cur.lastrowid)
