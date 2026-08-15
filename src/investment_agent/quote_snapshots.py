"""Scheduled intraday quote snapshots for Market Activity (Phase 1B Inc 11).

Stores one row per ticker per session slot per ET calendar day:
  pre_market  — before 9:30 ET (e.g. morning prep ~8:00 ET)
  at_open     — 9:30–9:44 ET
  plus_15m    — 9:45–9:59 ET

Refresh live / run_quote_snapshots upserts the active slot when called in-window.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, time
from zoneinfo import ZoneInfo

from investment_agent.regime import REGIME_SYMBOLS

ET = ZoneInfo("America/New_York")

SNAPSHOT_SLOTS = ("pre_market", "at_open", "plus_15m")

SNAPSHOT_SLOT_LABELS = {
    "pre_market": "Pre-market",
    "at_open": "At open (9:30 ET)",
    "plus_15m": "+15 min (9:45 ET)",
}

PRE_MARKET_START = time(4, 0)
MARKET_OPEN = time(9, 30)
OPEN_WINDOW_END = time(9, 45)
PLUS_15_WINDOW_END = time(10, 0)

INDEX_SYMBOLS = frozenset(REGIME_SYMBOLS)


def now_et() -> datetime:
    return datetime.now(ET)


def today_et_str(when: datetime | None = None) -> str:
    return (when or now_et()).strftime("%Y-%m-%d")


def snapshot_slot_for_time(when: datetime | None = None) -> str | None:
    """Return active snapshot slot for ``when``, or None outside snapshot windows."""
    dt = when or now_et()
    if dt.weekday() >= 5:
        return None
    t = dt.time()
    if PRE_MARKET_START <= t < MARKET_OPEN:
        return "pre_market"
    if MARKET_OPEN <= t < OPEN_WINDOW_END:
        return "at_open"
    if OPEN_WINDOW_END <= t < PLUS_15_WINDOW_END:
        return "plus_15m"
    return None


def collect_snapshot_symbols(
    conn: sqlite3.Connection,
    *,
    extra: set[str] | None = None,
) -> set[str]:
    """Symbols to snapshot: indices, top ranked live names, queue, open positions."""
    from investment_agent.journal import get_open_positions
    from investment_agent.trading_day import _live_ranked_candidates, get_top_pick

    symbols: set[str] = set(INDEX_SYMBOLS)
    for row in _live_ranked_candidates(conn, limit=10):
        symbols.add(row["ticker"])
    pick = get_top_pick(conn)
    if pick:
        symbols.add(pick["ticker"])
    rows = conn.execute(
        "SELECT DISTINCT ticker FROM queue_items WHERE state NOT IN ('closed')"
    ).fetchall()
    symbols.update(row["ticker"] for row in rows)
    for pos in get_open_positions(conn):
        symbols.add(pos["ticker"])
    if extra:
        symbols.update(s.upper() for s in extra)
    return {s.upper() for s in symbols if s}


def upsert_quote_snapshot(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    slot: str,
    ticker: str,
    captured_at: str,
    price: float,
    open_px: float | None = None,
    high: float | None = None,
    low: float | None = None,
    prev_close: float | None = None,
    source: str = "finnhub",
) -> None:
    conn.execute(
        """
        INSERT INTO quote_snapshots
          (session_date_et, slot, ticker, captured_at, price, open, high, low, prev_close, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_date_et, slot, ticker) DO UPDATE SET
          captured_at = excluded.captured_at,
          price = excluded.price,
          open = excluded.open,
          high = excluded.high,
          low = excluded.low,
          prev_close = excluded.prev_close,
          source = excluded.source
        """,
        (
            session_date_et,
            slot,
            ticker.upper(),
            captured_at,
            price,
            open_px,
            high,
            low,
            prev_close,
            source,
        ),
    )


def record_snapshots_from_quote_rows(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    slot: str,
    quote_rows: dict[str, dict],
) -> int:
    """Upsert snapshots for ``quote_rows`` keyed by ticker. Returns count written."""
    count = 0
    for ticker, row in quote_rows.items():
        price = row.get("price")
        if price is None:
            continue
        upsert_quote_snapshot(
            conn,
            session_date_et=session_date_et,
            slot=slot,
            ticker=ticker,
            captured_at=row.get("captured_at") or now_et().replace(microsecond=0).isoformat(),
            price=float(price),
            open_px=row.get("open"),
            high=row.get("high"),
            low=row.get("low"),
            prev_close=row.get("prev_close"),
            source=row.get("source", "finnhub"),
        )
        count += 1
    return count


def maybe_record_snapshots_after_refresh(
    conn: sqlite3.Connection,
    quote_rows: dict[str, dict],
    *,
    when: datetime | None = None,
    force_slot: str | None = None,
) -> dict:
    """If in a snapshot window (or ``force_slot``), upsert session snapshots."""
    dt = when or now_et()
    slot = force_slot or snapshot_slot_for_time(dt)
    if not slot:
        return {
            "recorded": False,
            "slot": None,
            "session_date_et": today_et_str(dt),
            "tickers": 0,
        }
    if slot not in SNAPSHOT_SLOTS:
        raise ValueError(f"Unknown snapshot slot: {slot}")
    session_date = today_et_str(dt)
    count = record_snapshots_from_quote_rows(
        conn,
        session_date_et=session_date,
        slot=slot,
        quote_rows=quote_rows,
    )
    return {
        "recorded": count > 0,
        "slot": slot,
        "slot_label": SNAPSHOT_SLOT_LABELS.get(slot, slot),
        "session_date_et": session_date,
        "tickers": count,
    }


def capture_quote_snapshots(
    conn: sqlite3.Connection,
    settings,
    *,
    slot: str | None = None,
    when: datetime | None = None,
    extra_symbols: set[str] | None = None,
) -> dict:
    """Fetch Finnhub quotes and store for the active or forced snapshot slot."""
    from investment_agent.db import insert_quote, log_ingest
    from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now

    dt = when or now_et()
    active_slot = slot or snapshot_slot_for_time(dt)
    if not active_slot:
        return {
            "ok": False,
            "error": "Outside snapshot windows — use --slot to force pre_market/at_open/plus_15m",
            "session_date_et": today_et_str(dt),
        }
    if not settings.finnhub_api_key:
        return {
            "ok": False,
            "error": "FINNHUB_API_KEY not set",
            "slot": active_slot,
        }

    symbols = collect_snapshot_symbols(conn, extra=extra_symbols)
    fh = FinnhubClient(settings.finnhub_api_key)
    quote_rows: dict[str, dict] = {}
    errors: list[str] = []
    try:
        for symbol in sorted(symbols):
            try:
                q = fh.get_quote(symbol)
                captured = fh_now()
                row = {
                    "ticker": symbol,
                    "captured_at": captured,
                    "price": float(q["c"]),
                    "open": float(q.get("o") or 0) or None,
                    "high": float(q.get("h") or 0) or None,
                    "low": float(q.get("l") or 0) or None,
                    "prev_close": float(q.get("pc") or 0) or None,
                    "source": "finnhub",
                }
                insert_quote(conn, row)
                quote_rows[symbol] = row
            except Exception as exc:
                errors.append(f"{symbol}: {exc}")
                log_ingest(conn, "finnhub", "error", f"snapshot {symbol}: {exc}")
    finally:
        fh.close()

    snap = maybe_record_snapshots_after_refresh(
        conn,
        quote_rows,
        when=dt,
        force_slot=active_slot,
    )
    return {
        "ok": len(quote_rows) > 0,
        "updated": sorted(quote_rows.keys()),
        "errors": errors,
        "snapshot": snap,
    }


def get_session_snapshot_status(
    conn: sqlite3.Connection,
    session_date_et: str | None = None,
) -> dict:
    """Summary of which slots are captured today and index prices at each slot."""
    day = session_date_et or today_et_str()
    rows = conn.execute(
        """
        SELECT slot, ticker, captured_at, price, open, high, low, prev_close
        FROM quote_snapshots
        WHERE session_date_et = ?
        ORDER BY slot, ticker
        """,
        (day,),
    ).fetchall()

    by_slot: dict[str, list[dict]] = {slot: [] for slot in SNAPSHOT_SLOTS}
    for row in rows:
        slot = row["slot"]
        if slot not in by_slot:
            by_slot[slot] = []
        by_slot[slot].append(
            {
                "ticker": row["ticker"],
                "captured_at": row["captured_at"],
                "price": float(row["price"]),
                "open": float(row["open"]) if row["open"] is not None else None,
                "high": float(row["high"]) if row["high"] is not None else None,
                "low": float(row["low"]) if row["low"] is not None else None,
                "prev_close": float(row["prev_close"]) if row["prev_close"] is not None else None,
            }
        )

    slots_meta = []
    for slot in SNAPSHOT_SLOTS:
        items = by_slot.get(slot) or []
        indices = [r for r in items if r["ticker"] in INDEX_SYMBOLS]
        slots_meta.append(
            {
                "slot": slot,
                "label": SNAPSHOT_SLOT_LABELS.get(slot, slot),
                "captured": len(items) > 0,
                "ticker_count": len(items),
                "captured_at": items[0]["captured_at"] if items else None,
                "indices": indices,
            }
        )

    active_slot = snapshot_slot_for_time()
    return {
        "session_date_et": day,
        "active_slot": active_slot,
        "active_slot_label": SNAPSHOT_SLOT_LABELS.get(active_slot) if active_slot else None,
        "slots": slots_meta,
        "complete": all(s["captured"] for s in slots_meta),
    }


def get_snapshots_for_tickers(
    conn: sqlite3.Connection,
    tickers: list[str],
    *,
    session_date_et: str | None = None,
) -> dict[str, dict[str, dict]]:
    """Return {ticker: {slot: quote_row}} for the session."""
    if not tickers:
        return {}
    day = session_date_et or today_et_str()
    placeholders = ",".join("?" for _ in tickers)
    rows = conn.execute(
        f"""
        SELECT slot, ticker, captured_at, price, open, high, low, prev_close
        FROM quote_snapshots
        WHERE session_date_et = ? AND ticker IN ({placeholders})
        """,
        [day, *[t.upper() for t in tickers]],
    ).fetchall()
    out: dict[str, dict[str, dict]] = {}
    for row in rows:
        sym = row["ticker"]
        out.setdefault(sym, {})[row["slot"]] = {
            "captured_at": row["captured_at"],
            "price": float(row["price"]),
            "open": float(row["open"]) if row["open"] is not None else None,
            "high": float(row["high"]) if row["high"] is not None else None,
            "low": float(row["low"]) if row["low"] is not None else None,
            "prev_close": float(row["prev_close"]) if row["prev_close"] is not None else None,
        }
    return out
