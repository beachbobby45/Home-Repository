"""Learning agent — daily feedback on trades and watchlist (Phase 5, no Claude)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

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


def _analyze_round_trips(conn: sqlite3.Connection) -> list[dict]:
    items: list[dict] = []
    for trip in get_completed_round_trips(conn, limit=30):
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
    return items


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
    """Build daily learning report from journal, queue, metrics, regime."""
    day = report_date or _today_et()
    quotes = get_latest_quotes(conn)

    active = _analyze_active_positions(conn, quotes)
    round_trips = _analyze_round_trips(conn)
    watchlist = _analyze_watchlist(conn, quotes)
    regime = _regime_stats(conn)
    multi_round = _multi_round_same_day(conn, day)

    eod_open = [a for a in active if a.get("queue_state") in ("in_trade", "eod")]

    highlights: list[str] = []
    if round_trips:
        wins = sum(1 for r in round_trips if r["net_pnl"] > 0)
        highlights.append(f"{len(round_trips)} round trip(s) logged; {wins} profitable after fees.")
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

    return {
        "report_date": day,
        "generated_at": _utc_now_iso(),
        "highlights": highlights,
        "active_positions": active,
        "round_trips": round_trips,
        "watchlist_insights": watchlist,
        "regime_stats": regime,
        "multi_round_same_day": multi_round,
        "eod_open_positions": eod_open,
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


def get_or_generate_learning_report(conn: sqlite3.Connection) -> dict:
    cached = get_learning_report(conn)
    if cached:
        return cached
    return generate_learning_report(conn)
