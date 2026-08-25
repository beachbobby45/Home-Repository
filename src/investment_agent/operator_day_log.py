"""Operator day log — attendance + NO TRADE / PASS / TRADED outcomes per session."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from investment_agent.journal import _parse_executed_at

ET = ZoneInfo("America/New_York")

OUTCOME_TRADED = "TRADED"
OUTCOME_NO_TRADE_SYSTEM = "NO_TRADE_SYSTEM"
OUTCOME_PASS_NO_SETUP = "PASS_NO_SETUP"
OUTCOME_NO_TRADE_OPERATOR = "NO_TRADE_OPERATOR"
OUTCOME_ATTENDED_ONLY = "ATTENDED_ONLY"

OUTCOMES = (
    OUTCOME_TRADED,
    OUTCOME_NO_TRADE_SYSTEM,
    OUTCOME_PASS_NO_SETUP,
    OUTCOME_NO_TRADE_OPERATOR,
    OUTCOME_ATTENDED_ONLY,
)

OUTCOME_LABELS: dict[str, str] = {
    OUTCOME_TRADED: "Traded (journal)",
    OUTCOME_NO_TRADE_SYSTEM: "NO TRADE (system)",
    OUTCOME_PASS_NO_SETUP: "Trade day — no entry",
    OUTCOME_NO_TRADE_OPERATOR: "NO TRADE (your choice)",
    OUTCOME_ATTENDED_ONLY: "Checked in",
}

SOURCE_AUTO_EOD = "auto_eod"
SOURCE_AUTO_JOURNAL = "auto_journal"
SOURCE_MANUAL = "manual"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today_et_str() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _executed_session_date_et(executed_at: str) -> str:
    try:
        return _parse_executed_at(executed_at).astimezone(ET).strftime("%Y-%m-%d")
    except ValueError:
        return executed_at[:10]


def session_date_et_from_executed_at(executed_at: str) -> str:
    return _executed_session_date_et(executed_at)


def journal_trade_count_for_session(conn: sqlite3.Connection, session_date_et: str) -> int:
    rows = conn.execute("SELECT executed_at FROM trade_journal").fetchall()
    return sum(1 for row in rows if _executed_session_date_et(row["executed_at"]) == session_date_et)


def _latest_market_activity(conn: sqlite3.Connection, session_date_et: str) -> dict | None:
    row = conn.execute(
        """
        SELECT score, band, allow_trade, summary
        FROM market_activity_evaluations
        WHERE session_date_et = ?
        ORDER BY captured_at DESC
        LIMIT 1
        """,
        (session_date_et,),
    ).fetchone()
    if not row:
        return None
    return {
        "score": int(row["score"]),
        "band": row["band"],
        "allow_trade": bool(row["allow_trade"]),
        "summary": row["summary"],
    }


def _resolve_top_pick_ticker(conn: sqlite3.Connection, session_date_et: str) -> str | None:
    from investment_agent.close_report import build_ranked_top20_for_date

    ranked = build_ranked_top20_for_date(conn, session_date_et)
    if not ranked:
        return None
    return ranked[0].get("ticker")


def _market_activity_for_session(conn: sqlite3.Connection, session_date_et: str) -> dict:
    stored = _latest_market_activity(conn, session_date_et)
    if stored:
        return stored
    from investment_agent.market_activity import evaluate_market_activity, market_activity_to_dict

    return market_activity_to_dict(evaluate_market_activity(conn, persist=False))


def infer_outcome_from_state(
    conn: sqlite3.Connection,
    session_date_et: str,
    *,
    market_activity: dict | None = None,
) -> tuple[str, dict]:
    """Return (outcome, context) when no manual override applies."""
    trade_count = journal_trade_count_for_session(conn, session_date_et)
    ma = market_activity or _market_activity_for_session(conn, session_date_et)
    top_pick = _resolve_top_pick_ticker(conn, session_date_et)
    ctx = {
        "market_activity_score": ma.get("score"),
        "market_activity_band": ma.get("band"),
        "allow_trade": bool(ma.get("allow_trade")),
        "top_pick_ticker": top_pick,
        "journal_trade_count": trade_count,
        "market_activity_summary": ma.get("summary"),
    }
    if trade_count > 0:
        return OUTCOME_TRADED, ctx
    if not ma.get("allow_trade"):
        return OUTCOME_NO_TRADE_SYSTEM, ctx
    return OUTCOME_PASS_NO_SETUP, ctx


def get_operator_day(conn: sqlite3.Connection, session_date_et: str) -> dict | None:
    row = conn.execute(
        """
        SELECT id, session_date_et, outcome, source, market_activity_score,
               market_activity_band, allow_trade, top_pick_ticker,
               journal_trade_count, notes, recorded_at, updated_at
        FROM operator_day_log
        WHERE session_date_et = ?
        """,
        (session_date_et,),
    ).fetchone()
    return _row_to_dict(row) if row else None


def list_operator_days(
    conn: sqlite3.Connection,
    *,
    limit: int = 60,
    since: str | None = None,
) -> list[dict]:
    if since:
        rows = conn.execute(
            """
            SELECT id, session_date_et, outcome, source, market_activity_score,
                   market_activity_band, allow_trade, top_pick_ticker,
                   journal_trade_count, notes, recorded_at, updated_at
            FROM operator_day_log
            WHERE session_date_et >= ?
            ORDER BY session_date_et DESC
            LIMIT ?
            """,
            (since, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, session_date_et, outcome, source, market_activity_score,
                   market_activity_band, allow_trade, top_pick_ticker,
                   journal_trade_count, notes, recorded_at, updated_at
            FROM operator_day_log
            ORDER BY session_date_et DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "session_date_et": row["session_date_et"],
        "outcome": row["outcome"],
        "outcome_label": OUTCOME_LABELS.get(row["outcome"], row["outcome"]),
        "source": row["source"],
        "market_activity_score": row["market_activity_score"],
        "market_activity_band": row["market_activity_band"],
        "allow_trade": bool(row["allow_trade"]) if row["allow_trade"] is not None else None,
        "top_pick_ticker": row["top_pick_ticker"],
        "journal_trade_count": row["journal_trade_count"],
        "notes": row["notes"],
        "recorded_at": row["recorded_at"],
        "updated_at": row["updated_at"],
    }


def _should_replace(existing: dict | None, *, new_outcome: str, new_source: str) -> bool:
    if existing is None:
        return True
    if new_outcome == OUTCOME_TRADED:
        return True
    if existing["outcome"] == OUTCOME_TRADED:
        return False
    if existing["source"] == SOURCE_MANUAL and new_source != SOURCE_MANUAL:
        return False
    return True


def upsert_operator_day(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    outcome: str,
    source: str,
    market_activity_score: int | None = None,
    market_activity_band: str | None = None,
    allow_trade: bool | None = None,
    top_pick_ticker: str | None = None,
    journal_trade_count: int | None = None,
    notes: str | None = None,
    force: bool = False,
) -> dict:
    outcome = outcome.upper().strip()
    if outcome not in OUTCOMES:
        raise ValueError(f"Invalid outcome {outcome!r}. Choose one of: {', '.join(OUTCOMES)}")

    existing = get_operator_day(conn, session_date_et)
    if not force and not _should_replace(existing, new_outcome=outcome, new_source=source):
        return {"ok": True, "skipped": True, "entry": existing}

    if journal_trade_count is None:
        journal_trade_count = journal_trade_count_for_session(conn, session_date_et)
    if outcome == OUTCOME_TRADED and journal_trade_count == 0:
        journal_trade_count = max(journal_trade_count, 1)

    now = _utc_now()
    if existing:
        conn.execute(
            """
            UPDATE operator_day_log
            SET outcome = ?, source = ?, market_activity_score = ?,
                market_activity_band = ?, allow_trade = ?, top_pick_ticker = ?,
                journal_trade_count = ?, notes = COALESCE(?, notes), updated_at = ?
            WHERE session_date_et = ?
            """,
            (
                outcome,
                source,
                market_activity_score,
                market_activity_band,
                None if allow_trade is None else (1 if allow_trade else 0),
                top_pick_ticker,
                journal_trade_count,
                notes,
                now,
                session_date_et,
            ),
        )
        entry = get_operator_day(conn, session_date_et)
        return {"ok": True, "updated": True, "entry": entry}

    conn.execute(
        """
        INSERT INTO operator_day_log
          (session_date_et, outcome, source, market_activity_score, market_activity_band,
           allow_trade, top_pick_ticker, journal_trade_count, notes, recorded_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_date_et,
            outcome,
            source,
            market_activity_score,
            market_activity_band,
            None if allow_trade is None else (1 if allow_trade else 0),
            top_pick_ticker,
            journal_trade_count,
            notes,
            now,
            now,
        ),
    )
    entry = get_operator_day(conn, session_date_et)
    return {"ok": True, "created": True, "entry": entry}


def record_operator_day_manual(
    conn: sqlite3.Connection,
    *,
    outcome: str,
    session_date_et: str | None = None,
    notes: str | None = None,
) -> dict:
    day = session_date_et or today_et_str()
    inferred_outcome, ctx = infer_outcome_from_state(conn, day)
    if outcome.upper().strip() == OUTCOME_TRADED and ctx["journal_trade_count"] == 0:
        raise ValueError("Cannot log TRADED — no journal entries on this session date")

    if outcome.upper().strip() == "NO_TRADE":
        outcome = (
            OUTCOME_NO_TRADE_SYSTEM
            if not ctx["allow_trade"]
            else OUTCOME_NO_TRADE_OPERATOR
        )

    return upsert_operator_day(
        conn,
        session_date_et=day,
        outcome=outcome,
        source=SOURCE_MANUAL,
        market_activity_score=ctx.get("market_activity_score"),
        market_activity_band=ctx.get("market_activity_band"),
        allow_trade=ctx.get("allow_trade"),
        top_pick_ticker=ctx.get("top_pick_ticker"),
        journal_trade_count=ctx["journal_trade_count"],
        notes=notes,
        force=True,
    )


def record_operator_day_from_journal(conn: sqlite3.Connection, session_date_et: str) -> dict:
    ctx_outcome, ctx = infer_outcome_from_state(conn, session_date_et)
    if ctx["journal_trade_count"] == 0:
        return {"ok": False, "skipped": True, "reason": "no_journal_trades"}
    return upsert_operator_day(
        conn,
        session_date_et=session_date_et,
        outcome=OUTCOME_TRADED,
        source=SOURCE_AUTO_JOURNAL,
        market_activity_score=ctx.get("market_activity_score"),
        market_activity_band=ctx.get("market_activity_band"),
        allow_trade=ctx.get("allow_trade"),
        top_pick_ticker=ctx.get("top_pick_ticker"),
        journal_trade_count=ctx["journal_trade_count"],
    )


def record_operator_day_from_eod(conn: sqlite3.Connection, session_date_et: str) -> dict:
    outcome, ctx = infer_outcome_from_state(conn, session_date_et)
    note = None
    if outcome == OUTCOME_NO_TRADE_SYSTEM:
        note = ctx.get("market_activity_summary") or "EOD auto — system NO TRADE"
    elif outcome == OUTCOME_PASS_NO_SETUP:
        top = ctx.get("top_pick_ticker")
        note = f"EOD auto — trade day, no journal entry{f'; top pick {top}' if top else ''}"
    elif outcome == OUTCOME_TRADED:
        note = f"EOD auto — {ctx['journal_trade_count']} journal leg(s)"
    return upsert_operator_day(
        conn,
        session_date_et=session_date_et,
        outcome=outcome,
        source=SOURCE_AUTO_EOD,
        market_activity_score=ctx.get("market_activity_score"),
        market_activity_band=ctx.get("market_activity_band"),
        allow_trade=ctx.get("allow_trade"),
        top_pick_ticker=ctx.get("top_pick_ticker"),
        journal_trade_count=ctx["journal_trade_count"],
        notes=note,
    )


def build_attendance_summary(
    conn: sqlite3.Connection,
    *,
    since: str | None = None,
    through: str | None = None,
    limit: int = 90,
) -> dict:
    """Attendance stats for operator discipline (e.g. September paper month)."""
    from investment_agent.close_report import _latest_ohlcv_date, _trading_days_in_range

    end = through or _latest_ohlcv_date(conn) or today_et_str()
    start = since or end[:8] + "01"
    if start > end:
        start, end = end, start
    trading_days = _trading_days_in_range(conn, start, end)
    if limit:
        trading_days = trading_days[-limit:]

    logged = {row["session_date_et"]: row for row in list_operator_days(conn, limit=500, since=start)}
    by_outcome: dict[str, int] = {k: 0 for k in OUTCOMES}
    attended: list[str] = []
    missing: list[str] = []

    for day in trading_days:
        entry = logged.get(day)
        if entry:
            attended.append(day)
            by_outcome[entry["outcome"]] = by_outcome.get(entry["outcome"], 0) + 1
        else:
            missing.append(day)

    return {
        "since": start,
        "through": end,
        "trading_days": len(trading_days),
        "attended_days": len(attended),
        "missing_days": len(missing),
        "missing_dates": missing,
        "by_outcome": by_outcome,
        "attendance_pct": round(100.0 * len(attended) / len(trading_days), 1) if trading_days else None,
    }
