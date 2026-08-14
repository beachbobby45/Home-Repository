"""Trade journal — manual E*TRADE fills (source of truth for cash and P&L)."""

from __future__ import annotations

import sqlite3
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE, ORIGINAL_BASIS

PT = ZoneInfo("America/Los_Angeles")


def today_pt_str() -> str:
    return datetime.now(PT).strftime("%Y-%m-%d")


def _parse_executed_at(executed_at: str) -> datetime:
    ts = executed_at.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=PT)
    return dt


def _executed_date_pt(executed_at: str) -> str:
    try:
        return _parse_executed_at(executed_at).astimezone(PT).strftime("%Y-%m-%d")
    except ValueError:
        return executed_at[:10]


def build_executed_at_pt(date_key: str, time_hm: str) -> str:
    """Combine YYYY-MM-DD and HH:MM as Pacific Time (E*TRADE audit log times)."""
    parts = time_hm.strip().split(":")
    if len(parts) < 2:
        raise ValueError("time must be HH:MM")
    hour, minute = int(parts[0]), int(parts[1])
    second = int(parts[2]) if len(parts) > 2 else 0
    y, m, d = map(int, date_key.split("-"))
    dt = datetime(y, m, d, hour, minute, second, tzinfo=PT)
    return dt.replace(microsecond=0).isoformat()


def normalize_executed_at(executed_at: str) -> str:
    """Store timezone-aware ISO; naive values are interpreted as Pacific Time."""
    return _parse_executed_at(executed_at).replace(microsecond=0).isoformat()


def resolve_executed_at(
    *,
    executed_at: str | None = None,
    executed_date: str | None = None,
    executed_time_pt: str | None = None,
) -> str | None:
    if executed_date and executed_time_pt:
        return build_executed_at_pt(executed_date, executed_time_pt)
    if executed_at:
        return normalize_executed_at(executed_at)
    return None


@dataclass(frozen=True)
class JournalEntry:
    id: int
    ticker: str
    side: str
    shares: float
    price: float
    fee: float
    executed_at: str
    notes: str | None
    queue_id: int | None


def _normalize_side(side: str) -> str:
    s = side.upper()
    if s not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    return s


def insert_trade(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    side: str,
    shares: float,
    price: float,
    fee: float | None = None,
    executed_at: str | None = None,
    notes: str | None = None,
    queue_id: int | None = None,
) -> int:
    if shares <= 0 or price <= 0:
        raise ValueError("shares and price must be positive")
    side_n = _normalize_side(side)
    default_fee = DEFAULT_BUY_FEE if side_n == "BUY" else DEFAULT_SELL_FEE
    when = (
        normalize_executed_at(executed_at)
        if executed_at
        else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    cur = conn.execute(
        """
        INSERT INTO trade_journal
          (ticker, side, shares, price, fee, executed_at, notes, queue_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticker.upper(),
            side_n,
            shares,
            price,
            fee if fee is not None else default_fee,
            when,
            notes,
            queue_id,
        ),
    )
    return int(cur.lastrowid)


def list_trades(conn: sqlite3.Connection, limit: int = 100) -> list[JournalEntry]:
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes, queue_id
        FROM trade_journal
        ORDER BY executed_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        JournalEntry(
            id=row["id"],
            ticker=row["ticker"],
            side=row["side"],
            shares=row["shares"],
            price=row["price"],
            fee=row["fee"],
            executed_at=row["executed_at"],
            notes=row["notes"],
            queue_id=row["queue_id"],
        )
        for row in rows
    ]


def journal_cash_balance(conn: sqlite3.Connection) -> float:
    """Cash available from journal activity starting at ORIGINAL_BASIS."""
    cash = ORIGINAL_BASIS
    rows = conn.execute(
        """
        SELECT side, shares, price, fee
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()
    for row in rows:
        notional = row["shares"] * row["price"]
        if row["side"] == "BUY":
            cash -= notional + row["fee"]
        else:
            cash += notional - row["fee"]
    return cash


def compute_total_fees(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT COALESCE(SUM(fee), 0) AS total FROM trade_journal").fetchone()
    return float(row["total"]) if row else 0.0


def compute_today_realized_net(conn: sqlite3.Connection, date_key: str | None = None) -> float:
    """FIFO matched round-trip P&L for closed trades on YYYY-MM-DD (Pacific Time)."""
    when = date_key or today_pt_str()
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()

    buys: dict[str, deque] = {}
    realized = 0.0

    for row in rows:
        if _executed_date_pt(row["executed_at"]) != when:
            continue
        ticker = row["ticker"]
        if row["side"] == "BUY":
            buys.setdefault(ticker, deque()).append(
                {"shares": float(row["shares"]), "price": float(row["price"]), "fee": float(row["fee"])}
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        queue = buys.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            realized += (sell_price - buy["price"]) * matched - buy_fee - sell_fee
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    return realized


def _week_start_pt(date_key: str | None = None) -> str:
    """Monday YYYY-MM-DD for the ISO week containing date_key (Pacific)."""
    when = date_key or today_pt_str()
    dt = datetime.strptime(when, "%Y-%m-%d").replace(tzinfo=PT)
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def compute_weekly_realized_net(conn: sqlite3.Connection, date_key: str | None = None) -> float:
    """FIFO round-trip P&L for sells from Monday PT through date_key (inclusive)."""
    when = date_key or today_pt_str()
    week_start = _week_start_pt(when)
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()

    buys: dict[str, deque] = {}
    realized = 0.0

    for row in rows:
        sell_day = _executed_date_pt(row["executed_at"])
        if row["side"] == "BUY":
            buys.setdefault(row["ticker"], deque()).append(
                {
                    "shares": float(row["shares"]),
                    "price": float(row["price"]),
                    "fee": float(row["fee"]),
                }
            )
            continue

        if sell_day < week_start or sell_day > when:
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        queue = buys.setdefault(row["ticker"], deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            realized += (sell_price - buy["price"]) * matched - buy_fee - sell_fee
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    return round(realized, 2)


def count_buys_today(conn: sqlite3.Connection, date_key: str | None = None) -> int:
    """Count BUY fills on the Pacific calendar day."""
    when = date_key or today_pt_str()
    rows = conn.execute(
        "SELECT executed_at FROM trade_journal WHERE side = 'BUY'"
    ).fetchall()
    return sum(1 for row in rows if _executed_date_pt(row["executed_at"]) == when)


def compute_monthly_realized_net(conn: sqlite3.Connection, month_key: str) -> float:
    """FIFO matched round-trip P&L for closed trades in YYYY-MM."""
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        WHERE strftime('%Y-%m', executed_at) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (month_key,),
    ).fetchall()

    buys: dict[str, deque] = {}
    realized = 0.0

    for row in rows:
        ticker = row["ticker"]
        if row["side"] == "BUY":
            buys.setdefault(ticker, deque()).append(
                {"shares": float(row["shares"]), "price": float(row["price"]), "fee": float(row["fee"])}
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        queue = buys.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            realized += (sell_price - buy["price"]) * matched - buy_fee - sell_fee
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    return realized


def trade_to_dict(entry: JournalEntry) -> dict:
    notional = entry.shares * entry.price
    return {
        "id": entry.id,
        "ticker": entry.ticker,
        "side": entry.side,
        "shares": entry.shares,
        "price": entry.price,
        "fee": entry.fee,
        "notional": notional,
        "executed_at": entry.executed_at,
        "notes": entry.notes,
        "queue_id": entry.queue_id,
    }


def _fifo_ledger(conn: sqlite3.Connection) -> tuple[list[dict], list[dict]]:
    """Return (open_lots, completed_round_trips) via FIFO matching."""
    rows = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, queue_id
        FROM trade_journal
        ORDER BY executed_at ASC, id ASC
        """
    ).fetchall()

    open_lots: dict[str, deque] = {}
    completed: list[dict] = []

    for row in rows:
        ticker = row["ticker"]
        if row["side"] == "BUY":
            open_lots.setdefault(ticker, deque()).append(
                {
                    "buy_id": row["id"],
                    "shares": float(row["shares"]),
                    "price": float(row["price"]),
                    "fee": float(row["fee"]),
                    "executed_at": row["executed_at"],
                    "queue_id": row["queue_id"],
                }
            )
            continue

        remaining = float(row["shares"])
        sell_price = float(row["price"])
        sell_shares = float(row["shares"])
        sell_fee_total = float(row["fee"])
        sell_at = row["executed_at"]
        sell_id = row["id"]
        sell_queue_id = row["queue_id"]
        queue = open_lots.setdefault(ticker, deque())

        while remaining > 1e-9 and queue:
            buy = queue[0]
            matched = min(remaining, buy["shares"])
            buy_fee = buy["fee"] * (matched / buy["shares"])
            sell_fee = sell_fee_total * (matched / sell_shares)
            gross = (sell_price - buy["price"]) * matched
            net = gross - buy_fee - sell_fee
            completed.append(
                {
                    "ticker": ticker,
                    "shares": matched,
                    "buy_price": buy["price"],
                    "sell_price": sell_price,
                    "buy_at": buy["executed_at"],
                    "sell_at": sell_at,
                    "buy_id": buy["buy_id"],
                    "sell_id": sell_id,
                    "queue_id": buy["queue_id"] or sell_queue_id,
                    "gross_pnl": gross,
                    "net_pnl": net,
                    "buy_fee": buy_fee,
                    "sell_fee": sell_fee,
                    "same_day": buy["executed_at"][:10] == sell_at[:10],
                }
            )
            remaining -= matched
            buy["shares"] -= matched
            buy["fee"] -= buy_fee
            if buy["shares"] <= 1e-9:
                queue.popleft()

    open_positions: list[dict] = []
    for ticker, lots in open_lots.items():
        for lot in lots:
            if lot["shares"] <= 1e-9:
                continue
            open_positions.append(
                {
                    "ticker": ticker,
                    "shares": lot["shares"],
                    "avg_cost": lot["price"],
                    "cost_basis": lot["shares"] * lot["price"] + lot["fee"],
                    "buy_at": lot["executed_at"],
                    "buy_id": lot["buy_id"],
                    "queue_id": lot["queue_id"],
                }
            )
    return open_positions, completed


def get_open_positions(conn: sqlite3.Connection) -> list[dict]:
    open_positions, _ = _fifo_ledger(conn)
    return open_positions


def get_completed_round_trips(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    _, completed = _fifo_ledger(conn)
    completed.sort(key=lambda r: r["sell_at"], reverse=True)
    return completed[:limit]


def clear_all_trades(conn: sqlite3.Connection) -> int:
    """Delete every row in trade_journal. Returns number of rows removed."""
    row = conn.execute("SELECT COUNT(*) AS c FROM trade_journal").fetchone()
    count = int(row["c"]) if row else 0
    conn.execute("DELETE FROM trade_journal")
    return count
