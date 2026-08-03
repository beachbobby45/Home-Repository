"""Stock team screener + rule-based analysis cards (Phase 2, no Claude)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.account import build_dashboard_summary
from investment_agent.journal import journal_cash_balance
from investment_agent.strategy import (
    ACTIVE_QUEUE_STATES,
    REGIME_ONLY_TICKERS,
    STOP_PCT,
    TARGET_PCT,
)


@dataclass(frozen=True)
class AnalysisCard:
    ticker: str
    last_quote: float
    avg_range_pct: float
    liquidity_cap: float
    suggested_size: float
    entry_price: float
    target_price: float
    stop_price: float
    thesis_summary: str


def _latest_metrics(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT m.*
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at
          FROM ticker_metrics
          GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        """
    ).fetchall()


def _active_queue_tickers(conn: sqlite3.Connection) -> set[str]:
    placeholders = ",".join("?" for _ in ACTIVE_QUEUE_STATES)
    rows = conn.execute(
        f"""
        SELECT DISTINCT ticker FROM queue_items
        WHERE state IN ({placeholders})
        """,
        ACTIVE_QUEUE_STATES,
    ).fetchall()
    return {row["ticker"] for row in rows}


def build_analysis_card(
    row: sqlite3.Row,
    tradable_cash: float,
) -> AnalysisCard | None:
    ticker = row["ticker"]
    if ticker in REGIME_ONLY_TICKERS:
        return None
    if not row["meets_liquidity_min"]:
        return None
    if not row["near_swing_target"]:
        return None

    last_quote = float(row["last_quote"] or row["last_close"] or 0)
    if last_quote <= 0:
        return None

    liquidity_cap = float(row["liquidity_cap"] or 0)
    suggested_size = min(liquidity_cap, tradable_cash)
    if suggested_size <= 0:
        return None

    target = last_quote * (1 + TARGET_PCT / 100)
    stop = last_quote * (1 - STOP_PCT / 100)
    avg_range = float(row["avg_range_pct"] or 0)
    swing_note = (
        "near ~3% swing target"
        if row["near_swing_target"]
        else f"avg range {avg_range:.1f}% (watch ~3%)"
    )

    thesis = (
        f"{ticker}: {swing_note}. Liquidity cap ${liquidity_cap:,.0f}. "
        f"Entry ~${last_quote:.2f} → target +{TARGET_PCT}% ${target:.2f}, "
        f"stop −{STOP_PCT}% ${stop:.2f}. "
        f"Size ${suggested_size:,.0f} (min of cap and tradable cash). "
        f"Execute in E*TRADE; log fill in journal."
    )

    return AnalysisCard(
        ticker=ticker,
        last_quote=last_quote,
        avg_range_pct=avg_range,
        liquidity_cap=liquidity_cap,
        suggested_size=suggested_size,
        entry_price=last_quote,
        target_price=target,
        stop_price=stop,
        thesis_summary=thesis,
    )


def screen_candidates(conn: sqlite3.Connection) -> list[AnalysisCard]:
    """Return qualified tickers sorted by avg range proximity to 3%."""
    sweeps_row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS t FROM sweep_history"
    ).fetchone()
    sweeps = float(sweeps_row["t"]) if sweeps_row else 0.0
    tradable = journal_cash_balance(conn) - sweeps

    cards: list[AnalysisCard] = []
    for row in _latest_metrics(conn):
        card = build_analysis_card(row, tradable)
        if card:
            cards.append(card)

    cards.sort(key=lambda c: abs(c.avg_range_pct - 3.0))
    return cards


def sync_queue_from_screener(conn: sqlite3.Connection, *, max_items: int = 5) -> dict:
    """
    Add top ranked live Step 3 passers to queue as 'watching' if not already active.
    Uses 14d period rank score (not range proximity alone).
    Respects regime block (returns message, does not add when blocked).
    """
    summary = build_dashboard_summary(conn)
    if summary.block_new_longs:
        return {
            "ok": False,
            "added": 0,
            "live_count": 0,
            "already_in_queue": 0,
            "message": "Regime blocks new longs — SPY/DIA/QQQ all down intraday.",
        }

    active = _active_queue_tickers(conn)
    from investment_agent.period_screener import build_ranked_candidates

    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live_ranked = [r for r in ranked if r.get("live_pass_today")]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    added_tickers: list[str] = []

    if live_ranked:
        live_count = len(live_ranked)
        pending = [r for r in live_ranked if r["ticker"] not in active]
        for row in pending[:max_items]:
            conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["ticker"],
                    row.get("suggested_size") or row.get("liquidity_cap") or 0,
                    row.get("entry_price"),
                    row.get("target_price"),
                    row.get("stop_price"),
                    row.get("avg_range_pct"),
                    row.get("liquidity_cap"),
                    row.get("thesis_summary") or "",
                    now,
                    now,
                ),
            )
            added_tickers.append(row["ticker"])
        live_names_source = live_ranked
    else:
        # No period history yet — fall back to live screener sorted by ~3% range
        live_cards = screen_candidates(conn)
        live_count = len(live_cards)
        pending = [c for c in live_cards if c.ticker not in active]
        for card in pending[:max_items]:
            conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card.ticker,
                    card.suggested_size,
                    card.entry_price,
                    card.target_price,
                    card.stop_price,
                    card.avg_range_pct,
                    card.liquidity_cap,
                    card.thesis_summary,
                    now,
                    now,
                ),
            )
            added_tickers.append(card.ticker)
        live_names_source = live_cards

    added = len(added_tickers)
    already = live_count - len(pending)

    if added:
        message = (
            f"Added {added} ticker(s) by 14d rank score: {', '.join(added_tickers)}."
        )
    elif not live_count:
        message = "No tickers pass Step 3 today — run ingest after loading your watchlist."
    elif already >= live_count:
        live_names = ", ".join(
            (r["ticker"] if isinstance(r, dict) else r.ticker)
            for r in live_names_source[:8]
        )
        suffix = f" ({live_names})" if live_names else ""
        message = (
            f"Nothing to add — all {live_count} live ranked candidate(s) "
            f"are already in the queue{suffix}."
        )
    else:
        message = "No new tickers to add (queue already has active picks)."

    return {
        "ok": True,
        "added": added,
        "live_count": live_count,
        "already_in_queue": already,
        "added_tickers": added_tickers,
        "message": message,
    }


def list_queue(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, ticker, state, suggested_size, entry_price, target_price,
               stop_price, avg_range_pct, liquidity_cap, thesis_summary,
               created_at, updated_at
        FROM queue_items
        ORDER BY
          CASE state
            WHEN 'in_trade' THEN 0
            WHEN 'alert' THEN 1
            WHEN 'armed' THEN 2
            WHEN 'approved' THEN 3
            WHEN 'watching' THEN 4
            WHEN 'eod' THEN 5
            WHEN 'runner' THEN 6
            ELSE 7
          END,
          updated_at DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def advance_queue_state(conn: sqlite3.Connection, item_id: int) -> dict:
    from investment_agent.strategy import NEXT_STATE, QUEUE_STATES

    row = conn.execute(
        "SELECT id, ticker, state FROM queue_items WHERE id = ?", (item_id,)
    ).fetchone()
    if not row:
        return {"ok": False, "error": "Queue item not found"}

    current = row["state"]
    nxt = NEXT_STATE.get(current)
    if nxt is None:
        return {"ok": False, "error": f"No next state after '{current}'"}

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn.execute(
        "UPDATE queue_items SET state = ?, updated_at = ? WHERE id = ?",
        (nxt, now, item_id),
    )
    return {"ok": True, "id": item_id, "from_state": current, "to_state": nxt}


def set_queue_state(conn: sqlite3.Connection, item_id: int, state: str) -> dict:
    if state not in QUEUE_STATES:
        return {"ok": False, "error": f"Invalid state: {state}"}
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    cur = conn.execute(
        "UPDATE queue_items SET state = ?, updated_at = ? WHERE id = ?",
        (state, now, item_id),
    )
    if cur.rowcount == 0:
        return {"ok": False, "error": "Queue item not found"}
    return {"ok": True, "id": item_id, "state": state}


def card_to_dict(card: AnalysisCard) -> dict:
    return {
        "ticker": card.ticker,
        "last_quote": card.last_quote,
        "avg_range_pct": card.avg_range_pct,
        "liquidity_cap": card.liquidity_cap,
        "suggested_size": card.suggested_size,
        "entry_price": card.entry_price,
        "target_price": card.target_price,
        "stop_price": card.stop_price,
        "thesis_summary": card.thesis_summary,
    }
