"""SQLite database schema and helpers (Phase 1 — no Claude)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "agent.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS watchlist (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL UNIQUE,
  sector TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ohlcv_daily (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  date TEXT NOT NULL,
  open REAL NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  close REAL NOT NULL,
  volume INTEGER NOT NULL,
  source TEXT NOT NULL DEFAULT 'finnhub',
  UNIQUE(ticker, date, source)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_ticker_date
  ON ohlcv_daily(ticker, date);

CREATE TABLE IF NOT EXISTS quotes (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  price REAL NOT NULL,
  open REAL,
  high REAL,
  low REAL,
  prev_close REAL,
  source TEXT NOT NULL DEFAULT 'finnhub'
);

CREATE INDEX IF NOT EXISTS idx_quotes_ticker_time
  ON quotes(ticker, captured_at);

CREATE TABLE IF NOT EXISTS macro_snapshots (
  id INTEGER PRIMARY KEY,
  captured_at TEXT NOT NULL,
  series_id TEXT NOT NULL,
  value REAL NOT NULL,
  observation_date TEXT NOT NULL,
  UNIQUE(series_id, observation_date)
);

CREATE TABLE IF NOT EXISTS ticker_metrics (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  computed_at TEXT NOT NULL,
  adv_dollar REAL,
  avg_range_pct REAL,
  liquidity_cap REAL,
  last_close REAL,
  last_quote REAL,
  meets_liquidity_min INTEGER NOT NULL DEFAULT 0,
  near_swing_target INTEGER NOT NULL DEFAULT 0,
  UNIQUE(ticker, computed_at)
);

CREATE TABLE IF NOT EXISTS ingest_log (
  id INTEGER PRIMARY KEY,
  run_at TEXT NOT NULL DEFAULT (datetime('now')),
  component TEXT NOT NULL,
  status TEXT NOT NULL,
  detail TEXT
);

CREATE TABLE IF NOT EXISTS regime_snapshots (
  id INTEGER PRIMARY KEY,
  captured_at TEXT NOT NULL UNIQUE,
  spy_change_pct REAL NOT NULL,
  dia_change_pct REAL NOT NULL,
  qqq_change_pct REAL NOT NULL,
  all_indices_down INTEGER NOT NULL DEFAULT 0,
  block_new_longs INTEGER NOT NULL DEFAULT 0,
  summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS jar_balances (
  jar_type TEXT PRIMARY KEY,
  balance REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sweep_history (
  id INTEGER PRIMARY KEY,
  month_key TEXT NOT NULL UNIQUE,
  realized_net REAL NOT NULL,
  management_amount REAL NOT NULL,
  tax_amount REAL NOT NULL,
  tax_rate REAL NOT NULL,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS queue_items (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'watching',
  suggested_size REAL,
  entry_price REAL,
  target_price REAL,
  stop_price REAL,
  avg_range_pct REAL,
  liquidity_cap REAL,
  thesis_summary TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_queue_items_ticker_state
  ON queue_items(ticker, state);

CREATE TABLE IF NOT EXISTS trade_journal (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  side TEXT NOT NULL CHECK(side IN ('BUY', 'SELL')),
  shares REAL NOT NULL,
  price REAL NOT NULL,
  fee REAL NOT NULL DEFAULT 7.0,
  executed_at TEXT NOT NULL,
  notes TEXT,
  queue_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (queue_id) REFERENCES queue_items(id)
);

CREATE INDEX IF NOT EXISTS idx_trade_journal_executed
  ON trade_journal(executed_at);

CREATE TABLE IF NOT EXISTS price_alerts (
  id INTEGER PRIMARY KEY,
  queue_id INTEGER,
  ticker TEXT NOT NULL,
  alert_type TEXT NOT NULL,
  entry_price REAL,
  current_price REAL,
  target_price REAL,
  stop_price REAL,
  pnl_pct REAL,
  message TEXT NOT NULL,
  acknowledged INTEGER NOT NULL DEFAULT 0,
  alert_date TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (queue_id) REFERENCES queue_items(id)
);

CREATE INDEX IF NOT EXISTS idx_price_alerts_active
  ON price_alerts(acknowledged, alert_date, ticker);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or DEFAULT_DB_PATH
    with connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    return path


def upsert_watchlist(conn: sqlite3.Connection, tickers: list[str]) -> None:
    for ticker in tickers:
        conn.execute(
            """
            INSERT INTO watchlist (ticker, active)
            VALUES (?, 1)
            ON CONFLICT(ticker) DO UPDATE SET active = 1
            """,
            (ticker.upper(),),
        )


def insert_ohlcv_rows(conn: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO ohlcv_daily
              (ticker, date, open, high, low, close, volume, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["ticker"],
                row["date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                row.get("source", "finnhub"),
            ),
        )
        count += 1
    return count


def insert_quote(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO quotes
          (ticker, captured_at, price, open, high, low, prev_close, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["ticker"],
            row["captured_at"],
            row["price"],
            row.get("open"),
            row.get("high"),
            row.get("low"),
            row.get("prev_close"),
            row.get("source", "finnhub"),
        ),
    )


def insert_macro(
    conn: sqlite3.Connection,
    series_id: str,
    observation_date: str,
    value: float,
    captured_at: str,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO macro_snapshots
          (captured_at, series_id, value, observation_date)
        VALUES (?, ?, ?, ?)
        """,
        (captured_at, series_id, value, observation_date),
    )


def insert_ticker_metrics(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO ticker_metrics
          (ticker, computed_at, adv_dollar, avg_range_pct, liquidity_cap,
           last_close, last_quote, meets_liquidity_min, near_swing_target)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["ticker"],
            row["computed_at"],
            row["adv_dollar"],
            row["avg_range_pct"],
            row["liquidity_cap"],
            row["last_close"],
            row["last_quote"],
            1 if row["meets_liquidity_min"] else 0,
            1 if row["near_swing_target"] else 0,
        ),
    )


def log_ingest(
    conn: sqlite3.Connection, component: str, status: str, detail: str = ""
) -> None:
    conn.execute(
        "INSERT INTO ingest_log (component, status, detail) VALUES (?, ?, ?)",
        (component, status, detail),
    )


def insert_regime_snapshot(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO regime_snapshots
          (captured_at, spy_change_pct, dia_change_pct, qqq_change_pct,
           all_indices_down, block_new_longs, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["captured_at"],
            row["spy_change_pct"],
            row["dia_change_pct"],
            row["qqq_change_pct"],
            1 if row["all_indices_down"] else 0,
            1 if row["block_new_longs"] else 0,
            row["summary"],
        ),
    )
