"""Pull broker ledger → SQLite mirror (Robinhood is source of truth)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.broker.client import BrokerAccountSnapshot, BrokerClient

ET = ZoneInfo("America/New_York")
BROKER_ROBINHOOD = "robinhood"


def _now() -> str:
    return datetime.now(ET).replace(microsecond=0).isoformat()


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def upsert_broker_account(
    conn: sqlite3.Connection,
    *,
    external_account_id: str,
    is_paper: bool = True,
    label: str | None = None,
    broker: str = BROKER_ROBINHOOD,
) -> int:
    now = _now()
    conn.execute(
        """
        INSERT INTO broker_accounts
          (broker, external_account_id, label, is_paper, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(broker, external_account_id) DO UPDATE SET
          label = COALESCE(excluded.label, broker_accounts.label),
          is_paper = excluded.is_paper
        """,
        (broker, external_account_id, label, 1 if is_paper else 0, now),
    )
    row = conn.execute(
        """
        SELECT id FROM broker_accounts
        WHERE broker = ? AND external_account_id = ?
        """,
        (broker, external_account_id),
    ).fetchone()
    return int(row["id"])


def latest_broker_balance(conn: sqlite3.Connection) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT b.*, a.external_account_id, a.is_paper, a.broker
        FROM broker_balances b
        JOIN broker_accounts a ON a.id = b.broker_account_id
        ORDER BY b.captured_at DESC, b.id DESC
        LIMIT 1
        """
    ).fetchone()
    return dict(row) if row else None


def sync_account_snapshot(
    conn: sqlite3.Connection,
    snapshot: BrokerAccountSnapshot,
    *,
    session_date_et: str | None = None,
    broker: str = BROKER_ROBINHOOD,
) -> dict[str, Any]:
    """Idempotent-ish sync: balances always append; fills/orders upsert by external id."""
    day = session_date_et or _today_et()
    captured = _now()
    account_id = upsert_broker_account(
        conn,
        external_account_id=snapshot.external_account_id,
        is_paper=snapshot.is_paper,
        broker=broker,
    )

    conn.execute(
        """
        INSERT INTO broker_balances
          (broker_account_id, captured_at, session_date_et, equity, cash, buying_power, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            account_id,
            captured,
            day,
            float(snapshot.equity),
            float(snapshot.cash),
            snapshot.buying_power,
            json.dumps(snapshot.raw) if snapshot.raw is not None else None,
        ),
    )

    # Replace positions snapshot for the session (delete+insert for this capture batch)
    for pos in snapshot.positions:
        conn.execute(
            """
            INSERT INTO broker_positions
              (broker_account_id, captured_at, session_date_et, ticker, qty, avg_cost, market_value, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account_id,
                captured,
                day,
                str(pos.get("ticker", "")).upper(),
                float(pos.get("qty") or 0),
                pos.get("avg_cost"),
                pos.get("market_value"),
                json.dumps(pos),
            ),
        )

    orders_upserted = 0
    for order in snapshot.open_orders:
        ext = str(order.get("external_order_id") or order.get("id") or "")
        if not ext:
            continue
        conn.execute(
            """
            INSERT INTO broker_orders (
              broker_account_id, external_order_id, session_date_et, ticker, side,
              order_type, status, limit_price, stop_price, qty, filled_qty,
              created_at, updated_at, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(broker_account_id, external_order_id) DO UPDATE SET
              status = excluded.status,
              filled_qty = excluded.filled_qty,
              updated_at = excluded.updated_at,
              raw_json = excluded.raw_json
            """,
            (
                account_id,
                ext,
                order.get("session_date_et") or day,
                str(order.get("ticker", "")).upper(),
                str(order.get("side", "")).lower(),
                order.get("order_type"),
                str(order.get("status", "unknown")),
                order.get("limit_price"),
                order.get("stop_price"),
                order.get("qty"),
                order.get("filled_qty"),
                order.get("created_at") or captured,
                captured,
                json.dumps(order),
            ),
        )
        orders_upserted += 1

    fills_upserted = 0
    for fill in snapshot.fills:
        ext = str(fill.get("external_fill_id") or fill.get("id") or "")
        if not ext:
            continue
        conn.execute(
            """
            INSERT INTO broker_fills (
              broker_account_id, external_fill_id, external_order_id, session_date_et,
              ticker, side, qty, price, fee, filled_at, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(broker_account_id, external_fill_id) DO UPDATE SET
              qty = excluded.qty,
              price = excluded.price,
              fee = excluded.fee,
              raw_json = excluded.raw_json
            """,
            (
                account_id,
                ext,
                fill.get("external_order_id"),
                fill.get("session_date_et") or day,
                str(fill.get("ticker", "")).upper(),
                str(fill.get("side", "")).lower(),
                float(fill.get("qty") or 0),
                float(fill.get("price") or 0),
                float(fill.get("fee") or 0),
                fill.get("filled_at") or captured,
                json.dumps(fill),
            ),
        )
        fills_upserted += 1

    return {
        "ok": True,
        "broker_account_id": account_id,
        "session_date_et": day,
        "captured_at": captured,
        "equity": float(snapshot.equity),
        "cash": float(snapshot.cash),
        "buying_power": snapshot.buying_power,
        "positions": len(snapshot.positions),
        "orders_upserted": orders_upserted,
        "fills_upserted": fills_upserted,
        "is_paper": bool(snapshot.is_paper),
    }


def sync_from_client(
    conn: sqlite3.Connection,
    client: BrokerClient,
    *,
    session_date_et: str | None = None,
) -> dict[str, Any]:
    snap = client.fetch_account_snapshot()
    return sync_account_snapshot(conn, snap, session_date_et=session_date_et)
