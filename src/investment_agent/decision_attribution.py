"""Decision-time attribution for Phase 1B learning (Inc 18).

Logs Market Activity, Confirmation, and authorization outcome when the system
evaluates or the human acts on a trade proposal.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from investment_agent.quote_snapshots import today_et_str


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def log_proposal_attribution(
    conn: sqlite3.Connection,
    *,
    event_type: str,
    session_date_et: str,
    ticker: str,
    proposal_id: int | None = None,
    market_activity: dict | None = None,
    exceptional_active: bool = False,
    human_verdict: str | None = None,
    human_rejection_reason: str | None = None,
    detail: dict | None = None,
) -> None:
    """Resolve MA + confirmation for a ticker and persist attribution."""
    from investment_agent.confirmation import evaluate_ticker_confirmation
    from investment_agent.market_activity import evaluate_market_activity, market_activity_to_dict
    from investment_agent.trading_day import now_et

    now = now_et()
    ma = market_activity or market_activity_to_dict(
        evaluate_market_activity(conn, when=now, persist=False)
    )
    conf = evaluate_ticker_confirmation(conn, ticker, market_activity=ma, when=now)
    log_decision_attribution(
        conn,
        event_type=event_type,
        session_date_et=session_date_et,
        ticker=ticker,
        proposal_id=proposal_id,
        market_activity=ma,
        confirmation=conf,
        exceptional_active=exceptional_active,
        human_verdict=human_verdict,
        human_rejection_reason=human_rejection_reason,
        detail=detail,
    )


def authorization_outcome(
    *,
    market_activity: dict | None,
    exceptional_active: bool = False,
) -> str:
    if exceptional_active:
        return "EXCEPTIONAL"
    if not market_activity:
        return "UNKNOWN"
    if market_activity.get("allow_trade"):
        return "TRADE"
    return "NO_TRADE"


def log_decision_attribution(
    conn: sqlite3.Connection,
    *,
    event_type: str,
    session_date_et: str | None = None,
    ticker: str | None = None,
    proposal_id: int | None = None,
    market_activity: dict | None = None,
    confirmation: dict | None = None,
    exceptional_active: bool = False,
    human_verdict: str | None = None,
    human_rejection_reason: str | None = None,
    detail: dict | None = None,
) -> None:
    ma = market_activity or {}
    conf = confirmation or {}
    conn.execute(
        """
        INSERT INTO decision_attribution_log
          (session_date_et, captured_at, event_type, ticker, proposal_id,
           market_activity_score, market_activity_band,
           confirmation_score, confirmation_passes,
           authorization_outcome, human_verdict, human_rejection_reason, detail_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_date_et or today_et_str(),
            _utc_now(),
            event_type,
            ticker.upper() if ticker else None,
            proposal_id,
            ma.get("score"),
            ma.get("band"),
            conf.get("score"),
            1 if conf.get("passes") else 0 if conf else None,
            authorization_outcome(market_activity=ma, exceptional_active=exceptional_active),
            human_verdict,
            human_rejection_reason,
            json.dumps(detail) if detail else None,
        ),
    )


def list_decision_attribution(
    conn: sqlite3.Connection,
    *,
    session_date_et: str | None = None,
    limit: int = 100,
) -> list[dict]:
    if session_date_et:
        rows = conn.execute(
            """
            SELECT *
            FROM decision_attribution_log
            WHERE session_date_et = ?
            ORDER BY captured_at DESC
            LIMIT ?
            """,
            (session_date_et, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT *
            FROM decision_attribution_log
            ORDER BY captured_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    detail = None
    if row["detail_json"]:
        try:
            detail = json.loads(row["detail_json"])
        except json.JSONDecodeError:
            detail = row["detail_json"]
    return {
        "id": row["id"],
        "session_date_et": row["session_date_et"],
        "captured_at": row["captured_at"],
        "event_type": row["event_type"],
        "ticker": row["ticker"],
        "proposal_id": row["proposal_id"],
        "market_activity_score": row["market_activity_score"],
        "market_activity_band": row["market_activity_band"],
        "confirmation_score": row["confirmation_score"],
        "confirmation_passes": bool(row["confirmation_passes"])
        if row["confirmation_passes"] is not None
        else None,
        "authorization_outcome": row["authorization_outcome"],
        "human_verdict": row["human_verdict"],
        "human_rejection_reason": row["human_rejection_reason"],
        "detail": detail,
    }


def build_market_activity_band_stats(
    conn: sqlite3.Connection,
    *,
    lookback_days: int = 30,
) -> dict:
    """Win-rate style stats grouped by market activity band (Inc 18)."""
    cutoff = (datetime.now(timezone.utc).replace(microsecond=0).isoformat())[:10]
    # Simple date filter on session_date_et
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    ET = ZoneInfo("America/New_York")
    start = (datetime.now(ET) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT d.market_activity_band, d.authorization_outcome,
               d.confirmation_score, d.confirmation_passes,
               p.outcome_net_pnl, p.status
        FROM decision_attribution_log d
        LEFT JOIN trade_proposals p ON p.id = d.proposal_id
        WHERE d.session_date_et >= ?
          AND d.event_type IN ('proposal_approve', 'live_refresh')
        ORDER BY d.captured_at DESC
        """,
        (start,),
    ).fetchall()

    bands: dict[str, dict] = {}
    for row in rows:
        band = row["market_activity_band"] or "unknown"
        bucket = bands.setdefault(
            band,
            {"band": band, "events": 0, "trade_days": 0, "with_outcome": 0, "wins": 0, "total_pnl": 0.0},
        )
        bucket["events"] += 1
        if row["authorization_outcome"] in ("TRADE", "EXCEPTIONAL"):
            bucket["trade_days"] += 1
        if row["outcome_net_pnl"] is not None:
            bucket["with_outcome"] += 1
            bucket["total_pnl"] += float(row["outcome_net_pnl"])
            if float(row["outcome_net_pnl"]) > 0:
                bucket["wins"] += 1

    for bucket in bands.values():
        n = bucket["with_outcome"]
        bucket["win_rate_pct"] = round(100.0 * bucket["wins"] / n, 1) if n else None
        bucket["avg_pnl"] = round(bucket["total_pnl"] / n, 2) if n else None

    return {"bands": list(bands.values()), "lookback_days": lookback_days}
