"""Intraday monitor — +1.13% target / −0.50% stop alerts (Phase 4, no Claude)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from investment_agent.strategy import ALERT_TYPES, MONITORED_STATES, STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")

NEAR_TARGET_BUFFER_PCT = 0.25  # alert when within 0.25% of target
NEAR_STOP_BUFFER_PCT = 0.10


@dataclass(frozen=True)
class MonitorEvaluation:
    queue_id: int
    ticker: str
    state: str
    entry_price: float
    current_price: float
    target_price: float
    stop_price: float
    pnl_pct: float
    alert_type: str | None
    message: str | None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def is_eod_window(when: datetime | None = None) -> bool:
    """After 3:45 PM ET on a weekday — remind to flatten intraday positions."""
    now = when or datetime.now(ET)
    if now.weekday() >= 5:
        return False
    return (now.hour, now.minute) >= (15, 45)


def pnl_pct(entry: float, current: float) -> float:
    if entry <= 0:
        return 0.0
    return ((current - entry) / entry) * 100.0


def target_stop_prices(entry: float) -> tuple[float, float]:
    target = entry * (1 + TARGET_PCT / 100)
    stop = entry * (1 - STOP_PCT / 100)
    return target, stop


def effective_entry_price(conn: sqlite3.Connection, queue_id: int, fallback: float) -> float:
    row = conn.execute(
        """
        SELECT price FROM trade_journal
        WHERE queue_id = ? AND side = 'BUY'
        ORDER BY executed_at DESC
        LIMIT 1
        """,
        (queue_id,),
    ).fetchone()
    if row and row["price"]:
        return float(row["price"])
    return fallback


def get_latest_quotes(conn: sqlite3.Connection) -> dict[str, float]:
    rows = conn.execute(
        """
        SELECT q.ticker, q.price
        FROM quotes q
        INNER JOIN (
          SELECT ticker, MAX(captured_at) AS max_at
          FROM quotes GROUP BY ticker
        ) latest ON q.ticker = latest.ticker AND q.captured_at = latest.max_at
        """
    ).fetchall()
    return {row["ticker"]: float(row["price"]) for row in rows}


def _classify_price_alert(
    *,
    state: str,
    entry: float,
    current: float,
    target: float,
    stop: float,
    eod: bool,
) -> tuple[str | None, str | None]:
    pct = pnl_pct(entry, current)

    if state in ("in_trade", "alert", "eod") and current >= target:
        return (
            "TARGET_HIT",
            f"Target +{TARGET_PCT}% hit — ${current:.2f} ≥ ${target:.2f} "
            f"(P&L {pct:+.2f}%). Consider taking profit in E*TRADE.",
        )

    if state in ("in_trade", "alert", "eod") and current <= stop:
        return (
            "STOP_HIT",
            f"Stop −{STOP_PCT}% hit — ${current:.2f} ≤ ${stop:.2f} "
            f"(P&L {pct:+.2f}%). Review exit in E*TRADE.",
        )

    if state == "in_trade" and eod:
        return (
            "EOD_FLATTEN",
            f"EOD reminder — {state} position open at ${current:.2f} "
            f"(P&L {pct:+.2f}%). Default rule: flat by close unless approved overnight.",
        )

    if state in ("armed", "alert", "in_trade"):
        if pct >= TARGET_PCT - NEAR_TARGET_BUFFER_PCT and current < target:
            return (
                "NEAR_TARGET",
                f"Approaching target — ${current:.2f}, P&L {pct:+.2f}% "
                f"(target ${target:.2f}).",
            )
        if pct <= -(STOP_PCT - NEAR_STOP_BUFFER_PCT) and current > stop:
            return (
                "NEAR_STOP",
                f"Approaching stop — ${current:.2f}, P&L {pct:+.2f}% "
                f"(stop ${stop:.2f}).",
            )

    return None, None


def evaluate_queue_item(
    conn: sqlite3.Connection,
    row: sqlite3.Row,
    quotes: dict[str, float],
    *,
    eod: bool | None = None,
) -> MonitorEvaluation | None:
    state = row["state"]
    if state not in MONITORED_STATES:
        return None

    ticker = row["ticker"]
    current = quotes.get(ticker)
    if current is None:
        return None

    fallback_entry = float(row["entry_price"] or current)
    entry = effective_entry_price(conn, int(row["id"]), fallback_entry)
    stored_target = float(row["target_price"]) if row["target_price"] else None
    stored_stop = float(row["stop_price"]) if row["stop_price"] else None
    target, stop = target_stop_prices(entry)
    if stored_target:
        target = stored_target
    if stored_stop:
        stop = stored_stop

    eod_flag = is_eod_window() if eod is None else eod
    alert_type, message = _classify_price_alert(
        state=state,
        entry=entry,
        current=current,
        target=target,
        stop=stop,
        eod=eod_flag,
    )

    return MonitorEvaluation(
        queue_id=int(row["id"]),
        ticker=ticker,
        state=state,
        entry_price=entry,
        current_price=current,
        target_price=target,
        stop_price=stop,
        pnl_pct=pnl_pct(entry, current),
        alert_type=alert_type,
        message=message,
    )


def _alert_exists_today(
    conn: sqlite3.Connection,
    queue_id: int | None,
    ticker: str,
    alert_type: str,
    alert_date: str,
) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM price_alerts
        WHERE alert_type = ?
          AND alert_date = ?
          AND acknowledged = 0
          AND (
            (queue_id IS NOT NULL AND queue_id = ?)
            OR (queue_id IS NULL AND ticker = ?)
          )
        LIMIT 1
        """,
        (alert_type, alert_date, queue_id, ticker),
    ).fetchone()
    return row is not None


def insert_alert(conn: sqlite3.Connection, ev: MonitorEvaluation, alert_date: str) -> int | None:
    if not ev.alert_type or not ev.message:
        return None
    if ev.alert_type not in ALERT_TYPES:
        return None
    if _alert_exists_today(conn, ev.queue_id, ev.ticker, ev.alert_type, alert_date):
        return None

    cur = conn.execute(
        """
        INSERT INTO price_alerts
          (queue_id, ticker, alert_type, entry_price, current_price,
           target_price, stop_price, pnl_pct, message, alert_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ev.queue_id,
            ev.ticker,
            ev.alert_type,
            ev.entry_price,
            ev.current_price,
            ev.target_price,
            ev.stop_price,
            ev.pnl_pct,
            ev.message,
            alert_date,
        ),
    )
    return int(cur.lastrowid)


def run_monitor_cycle(
    conn: sqlite3.Connection,
    quotes: dict[str, float] | None = None,
    *,
    eod: bool | None = None,
) -> dict:
    """Evaluate monitored queue items; persist new alerts."""
    quote_map = quotes if quotes is not None else get_latest_quotes(conn)
    alert_date = today_et()

    placeholders = ",".join("?" for _ in MONITORED_STATES)
    rows = conn.execute(
        f"""
        SELECT id, ticker, state, entry_price, target_price, stop_price
        FROM queue_items
        WHERE state IN ({placeholders})
        ORDER BY updated_at DESC
        """,
        MONITORED_STATES,
    ).fetchall()

    evaluations: list[MonitorEvaluation] = []
    new_alerts: list[int] = []
    missing_quotes: list[str] = []

    for row in rows:
        ticker = row["ticker"]
        if ticker not in quote_map:
            missing_quotes.append(ticker)
            continue
        ev = evaluate_queue_item(conn, row, quote_map, eod=eod)
        if ev:
            evaluations.append(ev)
            alert_id = insert_alert(conn, ev, alert_date)
            if alert_id:
                new_alerts.append(alert_id)

    return {
        "ok": True,
        "evaluated": len(evaluations),
        "new_alerts": len(new_alerts),
        "alert_ids": new_alerts,
        "missing_quotes": missing_quotes,
        "evaluations": [evaluation_to_dict(e) for e in evaluations],
    }


def list_active_alerts(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, queue_id, ticker, alert_type, entry_price, current_price,
               target_price, stop_price, pnl_pct, message, acknowledged,
               alert_date, created_at
        FROM price_alerts
        WHERE acknowledged = 0
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_all_alerts(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, queue_id, ticker, alert_type, entry_price, current_price,
               target_price, stop_price, pnl_pct, message, acknowledged,
               alert_date, created_at
        FROM price_alerts
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def acknowledge_alert(conn: sqlite3.Connection, alert_id: int) -> dict:
    cur = conn.execute(
        "UPDATE price_alerts SET acknowledged = 1 WHERE id = ? AND acknowledged = 0",
        (alert_id,),
    )
    if cur.rowcount == 0:
        return {"ok": False, "error": "Alert not found or already acknowledged"}
    return {"ok": True, "id": alert_id}


def enrich_queue_item(
    conn: sqlite3.Connection,
    item: dict,
    quotes: dict[str, float] | None = None,
) -> dict:
    """Add live price + P&L fields for dashboard display."""
    quote_map = quotes if quotes is not None else get_latest_quotes(conn)
    out = dict(item)
    ticker = item["ticker"]
    current = quote_map.get(ticker)
    out["current_price"] = current
    if current is None:
        out["pnl_pct"] = None
        out["monitor_status"] = "no_quote"
        return out

    entry = effective_entry_price(
        conn, int(item["id"]), float(item.get("entry_price") or current)
    )
    out["entry_price_effective"] = entry
    out["pnl_pct"] = pnl_pct(entry, current)
    target = float(item.get("target_price") or target_stop_prices(entry)[0])
    stop = float(item.get("stop_price") or target_stop_prices(entry)[1])
    out["distance_to_target_pct"] = pnl_pct(entry, target)
    out["distance_to_stop_pct"] = pnl_pct(entry, stop)

    if item["state"] in MONITORED_STATES:
        ev = evaluate_queue_item(
            conn,
            conn.execute(
                "SELECT id, ticker, state, entry_price, target_price, stop_price FROM queue_items WHERE id = ?",
                (item["id"],),
            ).fetchone(),
            quote_map,
            eod=False,
        )
        out["monitor_status"] = ev.alert_type.lower() if ev and ev.alert_type else "watching"
    else:
        out["monitor_status"] = "idle"
    return out


def evaluation_to_dict(ev: MonitorEvaluation) -> dict:
    return {
        "queue_id": ev.queue_id,
        "ticker": ev.ticker,
        "state": ev.state,
        "entry_price": ev.entry_price,
        "current_price": ev.current_price,
        "target_price": ev.target_price,
        "stop_price": ev.stop_price,
        "pnl_pct": ev.pnl_pct,
        "alert_type": ev.alert_type,
        "message": ev.message,
    }
