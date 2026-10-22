"""Ops audit log: TEST / PAPER / SYSTEM events.

TEST rows are visible in the Audit UI but never affect paper equity,
journal W/L, or Account P&L.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

KIND_TEST = "TEST"
KIND_PAPER = "PAPER"
KIND_SYSTEM = "SYSTEM"
VALID_KINDS = frozenset({KIND_TEST, KIND_PAPER, KIND_SYSTEM})

OPS_AUDIT_SQL = """
CREATE TABLE IF NOT EXISTS ops_audit_log (
  id INTEGER PRIMARY KEY,
  created_at TEXT NOT NULL,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  detail TEXT,
  payload_json TEXT,
  session_date_et TEXT,
  affects_pnl INTEGER NOT NULL DEFAULT 0,
  source TEXT
);

CREATE INDEX IF NOT EXISTS idx_ops_audit_created
  ON ops_audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ops_audit_kind
  ON ops_audit_log(kind, created_at DESC);
"""

LEDGER_SOURCE_KEY = "ledger_source"
LEDGER_SOURCE_JOURNAL = "journal"  # legacy journal cash (tests / pre-paper)
LEDGER_SOURCE_PAPER = "paper"  # internal $5k paper book (current ops)
LEDGER_SOURCE_ROBINHOOD = "robinhood"  # future: RH is source of truth
VALID_LEDGER_SOURCES = frozenset(
    {LEDGER_SOURCE_JOURNAL, LEDGER_SOURCE_PAPER, LEDGER_SOURCE_ROBINHOOD}
)


def ensure_ops_audit_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(OPS_AUDIT_SQL)


def get_ledger_source(conn: sqlite3.Connection) -> str:
    from investment_agent.account import get_setting

    # Default journal keeps unit/integration tests on historical cash math.
    # Paper worker / install script sets ledger_source=paper for Tony's Mac.
    raw = get_setting(conn, LEDGER_SOURCE_KEY, LEDGER_SOURCE_JOURNAL)
    return raw if raw in VALID_LEDGER_SOURCES else LEDGER_SOURCE_JOURNAL


def set_ledger_source(conn: sqlite3.Connection, source: str) -> str:
    from investment_agent.account import set_setting

    if source not in VALID_LEDGER_SOURCES:
        raise ValueError(f"Invalid ledger_source: {source}")
    set_setting(conn, LEDGER_SOURCE_KEY, source)
    return source


def log_audit_event(
    conn: sqlite3.Connection,
    *,
    kind: str,
    title: str,
    detail: str | None = None,
    payload: dict | list | None = None,
    session_date_et: str | None = None,
    source: str | None = None,
) -> int:
    ensure_ops_audit_schema(conn)
    if kind not in VALID_KINDS:
        raise ValueError(f"Invalid audit kind: {kind}")
    affects = 0 if kind == KIND_TEST else (1 if kind == KIND_PAPER else 0)
    now = datetime.now(ET).replace(microsecond=0).isoformat()
    cur = conn.execute(
        """
        INSERT INTO ops_audit_log
          (created_at, kind, title, detail, payload_json, session_date_et, affects_pnl, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            kind,
            title,
            detail,
            json.dumps(payload) if payload is not None else None,
            session_date_et,
            affects,
            source,
        ),
    )
    return int(cur.lastrowid)


PAPER_DAY_AUDIT_SOURCE = "paper_runner"


def paper_day_audit_exists(
    conn: sqlite3.Connection,
    session_date_et: str,
    *,
    source: str = PAPER_DAY_AUDIT_SOURCE,
) -> bool:
    ensure_ops_audit_schema(conn)
    row = conn.execute(
        """
        SELECT id FROM ops_audit_log
        WHERE kind = ? AND session_date_et = ? AND source = ?
        LIMIT 1
        """,
        (KIND_PAPER, session_date_et[:10], source),
    ).fetchone()
    return row is not None


def log_paper_day_complete(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    gate_log: dict[str, Any] | None,
    arms: list[dict[str, Any]] | None = None,
) -> int | None:
    """Idempotent PAPER audit when a paper day reaches a final gate status."""
    day = session_date_et[:10]
    if paper_day_audit_exists(conn, day):
        return None
    status = (gate_log or {}).get("status") or "unknown"
    ticker = (gate_log or {}).get("ticker")
    net = (gate_log or {}).get("net_pnl")
    title = f"PAPER day complete: {day} — {status}"
    detail_parts = [f"status={status}"]
    if ticker:
        detail_parts.append(f"ticker={ticker}")
    if net is not None:
        detail_parts.append(f"net_pnl={net}")
    return log_audit_event(
        conn,
        kind=KIND_PAPER,
        title=title,
        detail="; ".join(detail_parts),
        payload={
            "session_date_et": day,
            "gate": gate_log,
            "arms": arms or [],
        },
        session_date_et=day,
        source=PAPER_DAY_AUDIT_SOURCE,
    )


def list_audit_events(
    conn: sqlite3.Connection,
    *,
    kind: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    ensure_ops_audit_schema(conn)
    sql = "SELECT * FROM ops_audit_log WHERE 1=1"
    params: list[Any] = []
    if kind:
        sql += " AND kind = ?"
        params.append(kind)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(int(limit))
    rows = []
    for r in conn.execute(sql, params).fetchall():
        d = dict(r)
        if d.get("payload_json"):
            try:
                d["payload"] = json.loads(d["payload_json"])
            except json.JSONDecodeError:
                d["payload"] = None
        else:
            d["payload"] = None
        d["affects_pnl"] = bool(d.get("affects_pnl"))
        rows.append(d)
    return rows


def log_test_suite_results(
    conn: sqlite3.Connection,
    *,
    suite_name: str,
    passed: int,
    failed: int,
    total: int,
    details: list[dict[str, Any]] | None = None,
    notes: str | None = None,
) -> int:
    """Record a pytest/smoke run as TEST — never affects P&L."""
    ok = failed == 0 and total > 0
    title = f"TEST suite: {suite_name} — {'PASS' if ok else 'FAIL'} ({passed}/{total})"
    return log_audit_event(
        conn,
        kind=KIND_TEST,
        title=title,
        detail=notes or f"{passed} passed, {failed} failed, {total} total",
        payload={
            "suite": suite_name,
            "passed": passed,
            "failed": failed,
            "total": total,
            "ok": ok,
            "cases": details or [],
        },
        source="pytest",
    )
