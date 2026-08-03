"""Trade journal — manual E*TRADE fills (source of truth for cash and P&L)."""

from __future__ import annotations

import sqlite3
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE, ORIGINAL_BASIS


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
    when = executed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
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
    """FIFO matched round-trip P&L for closed trades on YYYY-MM-DD (UTC date prefix)."""
    when = date_key or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT ticker, side, shares, price, fee, executed_at
        FROM trade_journal
        WHERE date(executed_at) = date(?)
        ORDER BY executed_at ASC, id ASC
        """,
        (when,),
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
