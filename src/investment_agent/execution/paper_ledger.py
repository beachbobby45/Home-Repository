"""Internal paper ledger (no broker). Dual books: gate_approved + all_signals.

Settlement model (cash / unlevered):
  - Buys spend settled_cash.
  - Same-day sale proceeds go to unsettled_cash with settle_on = next trading day (T+1).
  - Before each session, unsettled rows with settle_on <= today move into settled_cash.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

PAPER_STARTING_CASH = 5_000.0
ACCOUNT_GATE = "gate_approved"
ACCOUNT_ALL = "all_signals"
PAPER_ACCOUNTS = (ACCOUNT_GATE, ACCOUNT_ALL)

PAPER_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS paper_accounts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  starting_cash REAL NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_balances (
  account_name TEXT NOT NULL PRIMARY KEY,
  settled_cash REAL NOT NULL,
  unsettled_cash REAL NOT NULL DEFAULT 0,
  equity REAL NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (account_name) REFERENCES paper_accounts(name)
);

CREATE TABLE IF NOT EXISTS paper_unsettled (
  id INTEGER PRIMARY KEY,
  account_name TEXT NOT NULL,
  amount REAL NOT NULL,
  from_session_date_et TEXT NOT NULL,
  settle_on_et TEXT NOT NULL,
  created_at TEXT NOT NULL,
  settled_at TEXT,
  FOREIGN KEY (account_name) REFERENCES paper_accounts(name)
);

CREATE INDEX IF NOT EXISTS idx_paper_unsettled_open
  ON paper_unsettled(account_name, settle_on_et) WHERE settled_at IS NULL;

CREATE TABLE IF NOT EXISTS paper_session_logs (
  id INTEGER PRIMARY KEY,
  session_date_et TEXT NOT NULL,
  account_name TEXT NOT NULL,
  ticker TEXT,
  allow_trade INTEGER,
  ma_score INTEGER,
  day_gate_mode TEXT,
  status TEXT NOT NULL,
  scenario TEXT,
  filled INTEGER NOT NULL DEFAULT 0,
  fill_ts TEXT,
  exit_ts TEXT,
  exit_reason TEXT,
  entry_price REAL,
  exit_price REAL,
  shares INTEGER,
  deploy REAL,
  net_pnl REAL,
  settled_cash_before REAL,
  settled_cash_after REAL,
  equity_after REAL,
  detail TEXT,
  payload_json TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(session_date_et, account_name),
  FOREIGN KEY (account_name) REFERENCES paper_accounts(name)
);

CREATE INDEX IF NOT EXISTS idx_paper_session_logs_date
  ON paper_session_logs(session_date_et DESC);

CREATE TABLE IF NOT EXISTS paper_fills (
  id INTEGER PRIMARY KEY,
  account_name TEXT NOT NULL,
  session_date_et TEXT NOT NULL,
  ticker TEXT NOT NULL,
  side TEXT NOT NULL,
  qty REAL NOT NULL,
  price REAL NOT NULL,
  fee REAL NOT NULL DEFAULT 0,
  filled_at TEXT NOT NULL,
  FOREIGN KEY (account_name) REFERENCES paper_accounts(name)
);
"""


def _now_et_iso() -> str:
    return datetime.now(ET).replace(microsecond=0).isoformat()


def ensure_paper_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(PAPER_TABLES_SQL)


def ensure_paper_accounts(
    conn: sqlite3.Connection,
    *,
    starting_cash: float = PAPER_STARTING_CASH,
) -> None:
    ensure_paper_schema(conn)
    now = _now_et_iso()
    for name in PAPER_ACCOUNTS:
        conn.execute(
            """
            INSERT OR IGNORE INTO paper_accounts (name, starting_cash, created_at)
            VALUES (?, ?, ?)
            """,
            (name, float(starting_cash), now),
        )
        row = conn.execute(
            "SELECT account_name FROM paper_balances WHERE account_name = ?",
            (name,),
        ).fetchone()
        if row is None:
            conn.execute(
                """
                INSERT INTO paper_balances
                  (account_name, settled_cash, unsettled_cash, equity, updated_at)
                VALUES (?, ?, 0, ?, ?)
                """,
                (name, float(starting_cash), float(starting_cash), now),
            )


def get_paper_balance(conn: sqlite3.Connection, account_name: str) -> dict[str, Any]:
    ensure_paper_accounts(conn)
    row = conn.execute(
        """
        SELECT account_name, settled_cash, unsettled_cash, equity, updated_at
        FROM paper_balances WHERE account_name = ?
        """,
        (account_name,),
    ).fetchone()
    assert row is not None
    return dict(row)


def next_trading_day_et(session_date: date | str) -> str:
    """Next weekday after session_date (simple exchange calendar; holidays ignored)."""
    if isinstance(session_date, str):
        d = date.fromisoformat(session_date[:10])
    else:
        d = session_date
    nxt = d + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return nxt.isoformat()


def settle_due_cash(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    account_name: str | None = None,
) -> dict[str, float]:
    """Move unsettled proceeds with settle_on <= session_date into settled_cash."""
    ensure_paper_accounts(conn)
    names = [account_name] if account_name else list(PAPER_ACCOUNTS)
    moved: dict[str, float] = {}
    now = _now_et_iso()
    for name in names:
        rows = conn.execute(
            """
            SELECT id, amount FROM paper_unsettled
            WHERE account_name = ?
              AND settled_at IS NULL
              AND settle_on_et <= ?
            """,
            (name, session_date_et[:10]),
        ).fetchall()
        total = 0.0
        for r in rows:
            total += float(r["amount"])
            conn.execute(
                "UPDATE paper_unsettled SET settled_at = ? WHERE id = ?",
                (now, r["id"]),
            )
        if total:
            bal = get_paper_balance(conn, name)
            settled = float(bal["settled_cash"]) + total
            unsettled = max(float(bal["unsettled_cash"]) - total, 0.0)
            equity = settled + unsettled
            conn.execute(
                """
                UPDATE paper_balances
                SET settled_cash = ?, unsettled_cash = ?, equity = ?, updated_at = ?
                WHERE account_name = ?
                """,
                (settled, unsettled, equity, now, name),
            )
        moved[name] = total
    return moved


def apply_round_trip(
    conn: sqlite3.Connection,
    *,
    account_name: str,
    session_date_et: str,
    ticker: str,
    shares: int,
    entry_price: float,
    exit_price: float,
    buy_fee: float,
    sell_fee: float,
    fill_ts: str | None,
    exit_ts: str | None,
) -> dict[str, Any]:
    """Debit settled for buy; credit sale proceeds to unsettled (T+1)."""
    ensure_paper_accounts(conn)
    settle_due_cash(conn, session_date_et=session_date_et, account_name=account_name)
    bal = get_paper_balance(conn, account_name)
    buy_notional = shares * entry_price + buy_fee
    sell_notional = shares * exit_price - sell_fee
    net = round(shares * (exit_price - entry_price) - buy_fee - sell_fee, 2)

    settled_before = float(bal["settled_cash"])
    if settled_before + 1e-9 < buy_notional:
        raise ValueError(
            f"Insufficient settled cash: need ${buy_notional:.2f}, have ${settled_before:.2f}"
        )

    now = _now_et_iso()
    settled_after_buy = settled_before - buy_notional
    unsettled = float(bal["unsettled_cash"]) + sell_notional
    equity = settled_after_buy + unsettled
    settle_on = next_trading_day_et(session_date_et)

    conn.execute(
        """
        UPDATE paper_balances
        SET settled_cash = ?, unsettled_cash = ?, equity = ?, updated_at = ?
        WHERE account_name = ?
        """,
        (settled_after_buy, unsettled, equity, now, account_name),
    )
    conn.execute(
        """
        INSERT INTO paper_unsettled
          (account_name, amount, from_session_date_et, settle_on_et, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (account_name, sell_notional, session_date_et[:10], settle_on, now),
    )
    conn.execute(
        """
        INSERT INTO paper_fills
          (account_name, session_date_et, ticker, side, qty, price, fee, filled_at)
        VALUES (?, ?, ?, 'buy', ?, ?, ?, ?)
        """,
        (
            account_name,
            session_date_et[:10],
            ticker.upper(),
            float(shares),
            float(entry_price),
            float(buy_fee),
            fill_ts or now,
        ),
    )
    conn.execute(
        """
        INSERT INTO paper_fills
          (account_name, session_date_et, ticker, side, qty, price, fee, filled_at)
        VALUES (?, ?, ?, 'sell', ?, ?, ?, ?)
        """,
        (
            account_name,
            session_date_et[:10],
            ticker.upper(),
            float(shares),
            float(exit_price),
            float(sell_fee),
            exit_ts or now,
        ),
    )
    return {
        "settled_before": settled_before,
        "settled_after": settled_after_buy,
        "unsettled_after": unsettled,
        "equity_after": equity,
        "net_pnl": net,
        "settle_on_et": settle_on,
        "buy_notional": buy_notional,
        "sell_notional": sell_notional,
    }


def upsert_session_log(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    ensure_paper_schema(conn)
    now = _now_et_iso()
    payload = row.get("payload_json")
    if payload is not None and not isinstance(payload, str):
        payload = json.dumps(payload)
    conn.execute(
        """
        INSERT INTO paper_session_logs (
          session_date_et, account_name, ticker, allow_trade, ma_score, day_gate_mode,
          status, scenario, filled, fill_ts, exit_ts, exit_reason, entry_price, exit_price,
          shares, deploy, net_pnl, settled_cash_before, settled_cash_after, equity_after,
          detail, payload_json, created_at, updated_at
        ) VALUES (
          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(session_date_et, account_name) DO UPDATE SET
          ticker = excluded.ticker,
          allow_trade = excluded.allow_trade,
          ma_score = excluded.ma_score,
          day_gate_mode = excluded.day_gate_mode,
          status = excluded.status,
          scenario = excluded.scenario,
          filled = excluded.filled,
          fill_ts = excluded.fill_ts,
          exit_ts = excluded.exit_ts,
          exit_reason = excluded.exit_reason,
          entry_price = excluded.entry_price,
          exit_price = excluded.exit_price,
          shares = excluded.shares,
          deploy = excluded.deploy,
          net_pnl = excluded.net_pnl,
          settled_cash_before = excluded.settled_cash_before,
          settled_cash_after = excluded.settled_cash_after,
          equity_after = excluded.equity_after,
          detail = excluded.detail,
          payload_json = excluded.payload_json,
          updated_at = excluded.updated_at
        """,
        (
            row["session_date_et"][:10],
            row["account_name"],
            row.get("ticker"),
            None if row.get("allow_trade") is None else (1 if row["allow_trade"] else 0),
            row.get("ma_score"),
            row.get("day_gate_mode"),
            row["status"],
            row.get("scenario"),
            1 if row.get("filled") else 0,
            row.get("fill_ts"),
            row.get("exit_ts"),
            row.get("exit_reason"),
            row.get("entry_price"),
            row.get("exit_price"),
            row.get("shares"),
            row.get("deploy"),
            row.get("net_pnl"),
            row.get("settled_cash_before"),
            row.get("settled_cash_after"),
            row.get("equity_after"),
            row.get("detail"),
            payload,
            now,
            now,
        ),
    )


def get_session_log(
    conn: sqlite3.Connection, session_date_et: str, account_name: str
) -> dict[str, Any] | None:
    ensure_paper_schema(conn)
    row = conn.execute(
        """
        SELECT * FROM paper_session_logs
        WHERE session_date_et = ? AND account_name = ?
        """,
        (session_date_et[:10], account_name),
    ).fetchone()
    return dict(row) if row else None


def list_session_logs(
    conn: sqlite3.Connection,
    *,
    account_name: str | None = None,
    since: str | None = None,
    limit: int = 90,
) -> list[dict[str, Any]]:
    ensure_paper_schema(conn)
    sql = "SELECT * FROM paper_session_logs WHERE 1=1"
    params: list[Any] = []
    if account_name:
        sql += " AND account_name = ?"
        params.append(account_name)
    if since:
        sql += " AND session_date_et >= ?"
        params.append(since[:10])
    sql += " ORDER BY session_date_et DESC, account_name LIMIT ?"
    params.append(int(limit))
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def paper_scoreboard(
    conn: sqlite3.Connection,
    *,
    since: str = "2026-10-20",
    until: str | None = None,
) -> dict[str, Any]:
    """Pass/fail snapshot for the Oct–Nov paper window."""
    ensure_paper_accounts(conn)
    until = until or date.today().isoformat()
    if until < since:
        # Before window start (e.g. Sunday Oct 18 before Mon Oct 20) — empty window
        until = since
    arms: dict[str, Any] = {}
    for name in PAPER_ACCOUNTS:
        logs = [
            r
            for r in list_session_logs(conn, account_name=name, since=since, limit=200)
            if r["session_date_et"] <= until
        ]
        fills = [r for r in logs if r.get("filled")]
        nets = [float(r["net_pnl"]) for r in fills if r.get("net_pnl") is not None]
        bal = get_paper_balance(conn, name)
        starting = float(
            conn.execute(
                "SELECT starting_cash FROM paper_accounts WHERE name = ?", (name,)
            ).fetchone()["starting_cash"]
        )
        equity = float(bal["equity"])
        dd = max(0.0, (starting - equity) / starting * 100.0) if starting else 0.0
        expectancy = (sum(nets) / len(nets)) if nets else None
        arms[name] = {
            "sessions_logged": len(logs),
            "fills": len(fills),
            "expectancy_per_fill": expectancy,
            "total_net_pnl": round(sum(nets), 2) if nets else 0.0,
            "equity": equity,
            "settled_cash": float(bal["settled_cash"]),
            "unsettled_cash": float(bal["unsettled_cash"]),
            "starting_cash": starting,
            "drawdown_pct_from_start": round(dd, 2),
            "growth_pct": round((equity / starting - 1.0) * 100.0, 2) if starting else 0.0,
        }

    primary = arms[ACCOUNT_GATE]
    criteria = {
        "min_fills": 30,
        "positive_expectancy": True,
        "max_drawdown_pct": 10.0,
        "beat_all_signals_optional": True,
        "beat_random_control": True,
    }
    pass_fills = primary["fills"] >= criteria["min_fills"]
    pass_exp = (primary["expectancy_per_fill"] or 0) > 0
    pass_dd = primary["drawdown_pct_from_start"] <= criteria["max_drawdown_pct"]

    from investment_agent.execution.random_control import get_random_control_summary

    rc = get_random_control_summary(conn)
    random_control_ok = None if not rc else rc.get("beats_random")
    notes = (
        "Primary arm is gate_approved (best_tradable_top3 by default). "
        "all_signals is the #1-only selection shadow (also ignores the day gate)."
    )
    if rc is None:
        notes += " Run scripts/run_random_pick_control.py to populate random_control_ok."
    elif random_control_ok is True:
        notes += " Random-pick control: #1 beats random (persisted)."
    elif random_control_ok is False:
        notes += " Random-pick control: #1 does not beat random."
    else:
        notes += " Random-pick control: inconclusive."

    return {
        "window": {"since": since, "until": until},
        "primary_arm": ACCOUNT_GATE,
        "arms": arms,
        "criteria": criteria,
        "checks": {
            "fills_ok": pass_fills,
            "expectancy_ok": pass_exp,
            "drawdown_ok": pass_dd,
            "random_control_ok": random_control_ok,
        },
        "random_control": rc,
        "paper_pass": pass_fills and pass_exp and pass_dd,
        "notes": notes,
    }
