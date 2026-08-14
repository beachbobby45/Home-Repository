"""Learning agent — daily feedback on trades and watchlist (Phase 5, no Claude)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.historical import evaluate_prior_day
from investment_agent.journal import get_completed_round_trips, get_open_positions
from investment_agent.liquidity import SWING_TARGET_PCT
from investment_agent.monitor import get_latest_quotes, pnl_pct
from investment_agent.strategy import STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _intraday_range_pct(open_px: float, high: float, low: float) -> float:
    if open_px <= 0:
        return 0.0
    return ((high - low) / open_px) * 100.0


def _queue_for(conn: sqlite3.Connection, queue_id: int | None) -> sqlite3.Row | None:
    if queue_id is None:
        return None
    return conn.execute(
        """
        SELECT id, ticker, state, entry_price, target_price, stop_price, avg_range_pct
        FROM queue_items WHERE id = ?
        """,
        (queue_id,),
    ).fetchone()


def _analyze_active_positions(conn: sqlite3.Connection, quotes: dict[str, float]) -> list[dict]:
    items: list[dict] = []
    for pos in get_open_positions(conn):
        ticker = pos["ticker"]
        current = quotes.get(ticker)
        entry = pos["avg_cost"]
        q = _queue_for(conn, pos.get("queue_id"))
        target = float(q["target_price"]) if q and q["target_price"] else entry * (1 + TARGET_PCT / 100)
        stop = float(q["stop_price"]) if q and q["stop_price"] else entry * (1 - STOP_PCT / 100)
        unrealized = None
        if current is not None:
            unrealized = (current - entry) * pos["shares"]
        items.append(
            {
                "ticker": ticker,
                "shares": pos["shares"],
                "entry_price": entry,
                "current_price": current,
                "unrealized_pnl": unrealized,
                "pnl_pct": pnl_pct(entry, current) if current else None,
                "target_price": target,
                "stop_price": stop,
                "queue_state": q["state"] if q else None,
                "eod_status": "open" if (q and q["state"] in ("in_trade", "eod")) else "unknown",
                "note": (
                    f"Open {pos['shares']:.0f} sh @ ${entry:.2f}"
                    + (f", unrealized ${unrealized:+.2f}" if unrealized is not None else "")
                ),
            }
        )
    return items


def _analyze_round_trips(conn: sqlite3.Connection, report_date: str | None = None) -> list[dict]:
    items: list[dict] = []
    for trip in get_completed_round_trips(conn, limit=50):
        if report_date and trip["sell_at"][:10] != report_date:
            continue
        q = _queue_for(conn, trip.get("queue_id"))
        rec_entry = float(q["entry_price"]) if q and q["entry_price"] else trip["buy_price"]
        target = float(q["target_price"]) if q and q["target_price"] else rec_entry * (1 + TARGET_PCT / 100)
        stop = float(q["stop_price"]) if q and q["stop_price"] else rec_entry * (1 - STOP_PCT / 100)
        entry_delta_pct = pnl_pct(rec_entry, trip["buy_price"])
        hit_target = trip["sell_price"] >= target - 0.001
        hit_stop = trip["sell_price"] <= stop + 0.001
        exit_vs_target = pnl_pct(target, trip["sell_price"])

        items.append(
            {
                "ticker": trip["ticker"],
                "shares": trip["shares"],
                "buy_price": trip["buy_price"],
                "sell_price": trip["sell_price"],
                "net_pnl": trip["net_pnl"],
                "same_day": trip["same_day"],
                "sell_date": trip["sell_at"][:10],
                "recommended_entry": rec_entry,
                "entry_delta_pct": entry_delta_pct,
                "target_price": target,
                "stop_price": stop,
                "hit_target": hit_target,
                "hit_stop": hit_stop,
                "exit_vs_target_pct": exit_vs_target,
                "note": (
                    f"{'Same-day' if trip['same_day'] else 'Multi-day'} round trip: "
                    f"net ${trip['net_pnl']:+.2f}, "
                    f"{'hit target' if hit_target else 'hit stop' if hit_stop else 'mid exit'}"
                ),
            }
        )
        if len(items) >= 30:
            break
    return items


def _journal_legs_for_date(conn: sqlite3.Connection, report_date: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (report_date,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "ticker": row["ticker"],
            "side": row["side"],
            "shares": row["shares"],
            "price": row["price"],
            "fee": row["fee"],
            "executed_at": row["executed_at"],
            "notes": row["notes"],
        }
        for row in rows
    ]


def _build_continual_learning(conn: sqlite3.Connection, *, lookback_days: int = 30) -> dict:
    """Aggregate journal + saved reports across recent days."""
    cutoff = (datetime.now(ET) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    trips = get_completed_round_trips(conn, limit=200)
    recent_trips = [t for t in trips if t["sell_at"][:10] >= cutoff]
    wins = sum(1 for t in recent_trips if t["net_pnl"] > 0)
    total_net = sum(t["net_pnl"] for t in recent_trips)
    same_day = sum(1 for t in recent_trips if t["same_day"])

    report_rows = conn.execute(
        """
        SELECT report_date, payload_json
        FROM learning_reports
        WHERE report_date >= ?
        ORDER BY report_date DESC
        """,
        (cutoff,),
    ).fetchall()

    range_errors: list[float] = []
    prior_screened = 0
    prior_targets = 0
    for row in report_rows:
        payload = json.loads(row["payload_json"])
        prior = payload.get("prior_day_evaluation")
        if not prior:
            continue
        summary = prior.get("summary") or {}
        prior_screened += summary.get("screened_count", 0)
        prior_targets += summary.get("simulated_targets", 0)
        for t in prior.get("all_tickers") or []:
            if t.get("range_delta_pct") is not None:
                range_errors.append(abs(float(t["range_delta_pct"])))

    saved_dates = [row["report_date"] for row in report_rows]
    return {
        "lookback_days": lookback_days,
        "cutoff_date": cutoff,
        "reports_saved": len(saved_dates),
        "saved_report_dates": saved_dates[:10],
        "journal": {
            "round_trips_closed": len(recent_trips),
            "win_rate_pct": round(100.0 * wins / max(len(recent_trips), 1), 1),
            "total_net_pnl": round(total_net, 2),
            "same_day_pct": round(100.0 * same_day / max(len(recent_trips), 1), 1),
        },
        "historical_accuracy": {
            "avg_range_error_pct": round(sum(range_errors) / len(range_errors), 2)
            if range_errors
            else None,
            "prior_day_screened_setups": prior_screened,
            "prior_day_simulated_targets": prior_targets,
        },
        "note": (
            f"Last {lookback_days}d: {len(recent_trips)} closed round trip(s), "
            f"{len(saved_dates)} saved learning report(s)."
        ),
    }


def list_learning_report_dates(conn: sqlite3.Connection, limit: int = 30) -> list[str]:
    rows = conn.execute(
        """
        SELECT report_date FROM learning_reports
        ORDER BY report_date DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [row["report_date"] for row in rows]


def _analyze_watchlist(conn: sqlite3.Connection, quotes: dict[str, float]) -> list[dict]:
    rows = conn.execute(
        """
        SELECT m.ticker, m.avg_range_pct, m.near_swing_target, m.last_quote,
               m.meets_liquidity_min, w.active
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        LEFT JOIN watchlist w ON w.ticker = m.ticker
        WHERE COALESCE(w.active, 1) = 1
        ORDER BY ABS(m.avg_range_pct - ?) ASC
        LIMIT 15
        """,
        (SWING_TARGET_PCT,),
    ).fetchall()

    active_tickers = {
        r["ticker"]
        for r in conn.execute(
            """
            SELECT DISTINCT ticker FROM queue_items
            WHERE state IN ('in_trade','alert','armed','eod')
            """
        ).fetchall()
    }

    items: list[dict] = []
    for row in rows:
        ticker = row["ticker"]
        if ticker in active_tickers:
            continue
        quote_row = conn.execute(
            """
            SELECT open, high, low, price FROM quotes q
            INNER JOIN (
              SELECT ticker, MAX(captured_at) AS max_at FROM quotes GROUP BY ticker
            ) l ON q.ticker = l.ticker AND q.captured_at = l.max_at
            WHERE q.ticker = ?
            """,
            (ticker,),
        ).fetchone()
        actual_range = None
        if quote_row and quote_row["open"]:
            actual_range = _intraday_range_pct(
                float(quote_row["open"]),
                float(quote_row["high"] or quote_row["price"]),
                float(quote_row["low"] or quote_row["price"]),
            )
        predicted = float(row["avg_range_pct"] or 0)
        items.append(
            {
                "ticker": ticker,
                "predicted_range_pct": predicted,
                "actual_range_pct": actual_range,
                "range_delta_pct": (
                    actual_range - predicted if actual_range is not None else None
                ),
                "near_swing_target": bool(row["near_swing_target"]),
                "meets_liquidity": bool(row["meets_liquidity_min"]),
                "last_quote": quotes.get(ticker, row["last_quote"]),
                "note": (
                    f"Avg range {predicted:.1f}% vs ~{SWING_TARGET_PCT}% target"
                    + (
                        f"; today ~{actual_range:.1f}%"
                        if actual_range is not None
                        else ""
                    )
                ),
            }
        )
    return items[:8]


def _regime_stats(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        """
        SELECT captured_at, block_new_longs
        FROM regime_snapshots
        ORDER BY captured_at DESC
        LIMIT 30
        """
    ).fetchall()
    blocked = sum(1 for r in rows if r["block_new_longs"])
    return {
        "snapshots_reviewed": len(rows),
        "blocked_days_recent": blocked,
        "latest_blocked": bool(rows[0]["block_new_longs"]) if rows else False,
    }


def _opportunity_score_bucket(score: float | int | None) -> str:
    if score is None:
        return "unknown"
    s = float(score)
    if s >= 85:
        return "85+"
    if s >= 75:
        return "75-85"
    if s >= 65:
        return "65-75"
    return "<65"


def _news_sentiment_bucket(score: float | None) -> str:
    if score is None:
        return "unknown"
    s = float(score)
    if s >= 60:
        return "positive"
    if s <= 40:
        return "negative"
    return "neutral"


def _parse_rejection_code(reason: str | None) -> str | None:
    if not reason:
        return None
    return reason.split(":")[0].strip().upper() or None


def _build_proposal_learning(conn: sqlite3.Connection, *, lookback_days: int = 30) -> dict:
    """Aggregate trade proposal outcomes, factor buckets, and rejection reasons."""
    cutoff = (datetime.now(ET) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT id, ticker, session_date_et, opportunity_score, factor_scores_json,
               status, human_verdict, human_rejection_reason, outcome_net_pnl,
               risk_verdict, model_version, journal_buy_id, journal_sell_id, created_at
        FROM trade_proposals
        WHERE session_date_et >= ?
        ORDER BY created_at DESC
        """,
        (cutoff,),
    ).fetchall()

    rejection_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    opp_buckets: dict[str, list[sqlite3.Row]] = {"65-75": [], "75-85": [], "85+": []}
    sent_buckets: dict[str, list[sqlite3.Row]] = {
        "negative": [],
        "neutral": [],
        "positive": [],
    }
    outcomes: list[dict] = []

    for row in rows:
        status = row["status"] or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

        code = _parse_rejection_code(row["human_rejection_reason"])
        if code:
            rejection_counts[code] = rejection_counts.get(code, 0) + 1

        bucket = _opportunity_score_bucket(row["opportunity_score"])
        if bucket in opp_buckets:
            opp_buckets[bucket].append(row)

        try:
            factors = json.loads(row["factor_scores_json"] or "{}")
        except json.JSONDecodeError:
            factors = {}
        sent_bucket = _news_sentiment_bucket(factors.get("news_sentiment"))
        if sent_bucket in sent_buckets:
            sent_buckets[sent_bucket].append(row)

        if row["outcome_net_pnl"] is not None or row["journal_buy_id"]:
            outcomes.append(
                {
                    "proposal_id": row["id"],
                    "ticker": row["ticker"],
                    "session_date_et": row["session_date_et"],
                    "opportunity_score": row["opportunity_score"],
                    "status": status,
                    "outcome_net_pnl": row["outcome_net_pnl"],
                    "human_verdict": row["human_verdict"],
                    "risk_verdict": row["risk_verdict"],
                    "model_version": row["model_version"],
                }
            )

    def _bucket_stats(items: list[sqlite3.Row]) -> dict:
        with_outcome = [r for r in items if r["outcome_net_pnl"] is not None]
        wins = sum(1 for r in with_outcome if float(r["outcome_net_pnl"]) > 0)
        avg_pnl = (
            round(sum(float(r["outcome_net_pnl"]) for r in with_outcome) / len(with_outcome), 2)
            if with_outcome
            else None
        )
        return {
            "proposal_count": len(items),
            "with_outcome": len(with_outcome),
            "win_rate_pct": round(100.0 * wins / max(len(with_outcome), 1), 1),
            "avg_outcome_pnl": avg_pnl,
        }

    opportunity_bucket_stats = {
        name: _bucket_stats(items) for name, items in opp_buckets.items()
    }
    news_sentiment_bucket_stats = {
        name: _bucket_stats(items) for name, items in sent_buckets.items()
    }

    approved = sum(1 for r in rows if r["human_verdict"] == "approved")
    rejected = sum(1 for r in rows if r["human_verdict"] == "rejected")
    executed = sum(1 for r in rows if r["status"] in ("executed", "closed"))

    questions: list[str] = []
    if any(v["with_outcome"] for v in opportunity_bucket_stats.values()):
        best = max(
            opportunity_bucket_stats.items(),
            key=lambda kv: kv[1]["win_rate_pct"] if kv[1]["with_outcome"] else -1,
        )
        questions.append(
            f"Highest win rate by opportunity bucket: {best[0]} "
            f"({best[1]['win_rate_pct']}% over {best[1]['with_outcome']} closed)."
        )
    if any(v["with_outcome"] for v in news_sentiment_bucket_stats.values()):
        pos = news_sentiment_bucket_stats.get("positive", {})
        neg = news_sentiment_bucket_stats.get("negative", {})
        if pos.get("with_outcome") and neg.get("with_outcome"):
            questions.append(
                f"News sentiment positive bucket win rate {pos['win_rate_pct']}% "
                f"vs negative {neg['win_rate_pct']}%."
            )
    if rejection_counts:
        top_reason = max(rejection_counts.items(), key=lambda kv: kv[1])
        questions.append(
            f"Most common rejection: {top_reason[0]} ({top_reason[1]} time(s))."
        )

    return {
        "lookback_days": lookback_days,
        "cutoff_date": cutoff,
        "total_proposals": len(rows),
        "approved_count": approved,
        "rejected_count": rejected,
        "executed_count": executed,
        "status_counts": status_counts,
        "rejection_reason_counts": rejection_counts,
        "opportunity_bucket_stats": opportunity_bucket_stats,
        "news_sentiment_bucket_stats": news_sentiment_bucket_stats,
        "proposal_outcomes": outcomes[:20],
        "factor_questions": questions,
        "note": (
            f"{len(rows)} proposal(s) since {cutoff}; "
            f"{approved} approved, {rejected} rejected, {executed} executed/closed."
        ),
    }


def _multi_round_same_day(conn: sqlite3.Connection, report_date: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT ticker, COUNT(*) AS legs
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        GROUP BY ticker
        HAVING legs >= 2
        ORDER BY legs DESC
        """,
        (report_date,),
    ).fetchall()
    return [{"ticker": r["ticker"], "legs": r["legs"]} for r in rows]


def generate_learning_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
) -> dict:
    """Build daily learning report from journal, queue, metrics, regime, and history."""
    day = report_date or _today_et()
    quotes = get_latest_quotes(conn)

    active = _analyze_active_positions(conn, quotes)
    today_round_trips = _analyze_round_trips(conn, report_date=day)
    recent_round_trips = _analyze_round_trips(conn)
    watchlist = _analyze_watchlist(conn, quotes)
    regime = _regime_stats(conn)
    multi_round = _multi_round_same_day(conn, day)
    today_journal = _journal_legs_for_date(conn, day)
    prior_day = evaluate_prior_day(conn, reference_date=day)
    continual = _build_continual_learning(conn)
    proposal_learning = _build_proposal_learning(conn)

    eod_open = [a for a in active if a.get("queue_state") in ("in_trade", "eod")]

    highlights: list[str] = []
    if today_round_trips:
        wins = sum(1 for r in today_round_trips if r["net_pnl"] > 0)
        highlights.append(
            f"Today: {len(today_round_trips)} round trip(s) closed; {wins} profitable after fees."
        )
    elif recent_round_trips:
        wins = sum(1 for r in recent_round_trips if r["net_pnl"] > 0)
        highlights.append(
            f"Recent: {len(recent_round_trips)} round trip(s) logged; {wins} profitable after fees."
        )
    if today_journal:
        highlights.append(f"Today: {len(today_journal)} journal leg(s) logged.")
    if prior_day and prior_day.get("summary"):
        s = prior_day["summary"]
        highlights.append(
            f"Prior day ({prior_day['eval_date']}): {s['screened_count']} screener match(es), "
            f"{s['simulated_targets']} simulated target(s), {s['simulated_stops']} stop(s)."
        )
    if continual["journal"]["round_trips_closed"]:
        highlights.append(
            f"Continual ({continual['lookback_days']}d): "
            f"{continual['journal']['win_rate_pct']}% win rate, "
            f"net ${continual['journal']['total_net_pnl']:+.2f}."
        )
    if active:
        highlights.append(f"{len(active)} open position(s) — review target/stop and EOD flat rule.")
    if eod_open:
        highlights.append(f"{len(eod_open)} position(s) still open near session end — confirm flat or overnight approval.")
    if multi_round:
        names = ", ".join(f"{m['ticker']}({m['legs']} legs)" for m in multi_round)
        highlights.append(f"Multi-leg same-day activity: {names}.")
    if regime["blocked_days_recent"]:
        highlights.append(
            f"Regime blocked new longs on {regime['blocked_days_recent']} of last "
            f"{regime['snapshots_reviewed']} snapshots."
        )
    if watchlist:
        near = [w["ticker"] for w in watchlist if w["near_swing_target"]][:3]
        if near:
            highlights.append(f"Watchlist near ~3% swing: {', '.join(near)}.")
    if proposal_learning["total_proposals"]:
        highlights.append(proposal_learning["note"])
        highlights.extend(proposal_learning.get("factor_questions") or [])

    return {
        "report_date": day,
        "generated_at": _utc_now_iso(),
        "highlights": highlights,
        "active_positions": active,
        "round_trips": recent_round_trips,
        "today_round_trips": today_round_trips,
        "today_journal": today_journal,
        "watchlist_insights": watchlist,
        "regime_stats": regime,
        "multi_round_same_day": multi_round,
        "eod_open_positions": eod_open,
        "prior_day_evaluation": prior_day,
        "continual_learning": continual,
        "proposal_learning": proposal_learning,
        "claude_ready": False,
    }


def save_learning_report(conn: sqlite3.Connection, report: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO learning_reports (report_date, generated_at, payload_json)
        VALUES (?, ?, ?)
        ON CONFLICT(report_date) DO UPDATE SET
          generated_at = excluded.generated_at,
          payload_json = excluded.payload_json
        """,
        (report["report_date"], report["generated_at"], json.dumps(report)),
    )
    row = conn.execute(
        "SELECT id FROM learning_reports WHERE report_date = ?",
        (report["report_date"],),
    ).fetchone()
    return int(row["id"]) if row else int(cur.lastrowid)


def get_learning_report(conn: sqlite3.Connection, report_date: str | None = None) -> dict | None:
    day = report_date or _today_et()
    row = conn.execute(
        "SELECT payload_json FROM learning_reports WHERE report_date = ?",
        (day,),
    ).fetchone()
    if row:
        return json.loads(row["payload_json"])
    return None


def get_or_generate_learning_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
) -> dict:
    day = report_date or _today_et()
    cached = get_learning_report(conn, day)
    if cached:
        return cached
    return generate_learning_report(conn, report_date=day)
