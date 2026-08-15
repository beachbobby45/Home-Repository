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
  source TEXT DEFAULT 'manual',
  added_via TEXT DEFAULT 'manual',
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

CREATE TABLE IF NOT EXISTS quote_snapshots (
  id INTEGER PRIMARY KEY,
  session_date_et TEXT NOT NULL,
  slot TEXT NOT NULL,
  ticker TEXT NOT NULL,
  captured_at TEXT NOT NULL,
  price REAL NOT NULL,
  open REAL,
  high REAL,
  low REAL,
  prev_close REAL,
  source TEXT NOT NULL DEFAULT 'finnhub',
  UNIQUE(session_date_et, slot, ticker)
);

CREATE INDEX IF NOT EXISTS idx_quote_snapshots_session
  ON quote_snapshots(session_date_et, slot);

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
  proposal_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (queue_id) REFERENCES queue_items(id),
  FOREIGN KEY (proposal_id) REFERENCES trade_proposals(id)
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

CREATE TABLE IF NOT EXISTS learning_reports (
  id INTEGER PRIMARY KEY,
  report_date TEXT NOT NULL UNIQUE,
  generated_at TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screener_runs (
  id INTEGER PRIMARY KEY,
  run_type TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  params_json TEXT NOT NULL,
  summary_json TEXT,
  status TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS period_screener_hits (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  hit_date TEXT NOT NULL,
  predicted_range_pct REAL,
  actual_range_pct REAL,
  simulated_outcome TEXT,
  would_screen INTEGER NOT NULL DEFAULT 1,
  days_screened INTEGER NOT NULL DEFAULT 0,
  hit_rate_pct REAL,
  score REAL,
  FOREIGN KEY (run_id) REFERENCES screener_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_period_hits_run
  ON period_screener_hits(run_id, score DESC);

CREATE TABLE IF NOT EXISTS rank_snapshots (
  id INTEGER PRIMARY KEY,
  snapshot_date TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  ranked_json TEXT NOT NULL,
  top_n INTEGER NOT NULL DEFAULT 20
);

CREATE TABLE IF NOT EXISTS close_reports (
  id INTEGER PRIMARY KEY,
  report_date TEXT NOT NULL,
  report_type TEXT NOT NULL CHECK(report_type IN ('daily', 'weekly')),
  generated_at TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  UNIQUE(report_date, report_type)
);

CREATE TABLE IF NOT EXISTS news_headlines (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL,
  headline_hash TEXT NOT NULL,
  published_at TEXT NOT NULL,
  headline TEXT NOT NULL,
  summary TEXT,
  source TEXT,
  url TEXT,
  ingested_at TEXT NOT NULL,
  UNIQUE(ticker, headline_hash)
);

CREATE INDEX IF NOT EXISTS idx_news_ticker_time
  ON news_headlines(ticker, published_at);

CREATE TABLE IF NOT EXISTS trade_proposals (
  id INTEGER PRIMARY KEY,
  proposal_uuid TEXT NOT NULL UNIQUE,
  strategy_version TEXT NOT NULL,
  model_version TEXT NOT NULL,
  created_at TEXT NOT NULL,
  valid_until TEXT,
  session_date_et TEXT NOT NULL,
  ticker TEXT NOT NULL,
  direction TEXT NOT NULL DEFAULT 'long',
  opportunity_score REAL NOT NULL,
  factor_scores_json TEXT NOT NULL,
  plan_json TEXT NOT NULL,
  risk_verdict TEXT NOT NULL,
  risk_checks_json TEXT NOT NULL,
  risk_rejection_reason TEXT,
  human_verdict TEXT,
  human_rejection_reason TEXT,
  human_approved_at TEXT,
  explanation TEXT,
  explanation_short TEXT,
  status TEXT NOT NULL,
  journal_buy_id INTEGER,
  journal_sell_id INTEGER,
  outcome_net_pnl REAL,
  outcome_exit_reason TEXT,
  FOREIGN KEY (journal_buy_id) REFERENCES trade_journal(id),
  FOREIGN KEY (journal_sell_id) REFERENCES trade_journal(id)
);

CREATE INDEX IF NOT EXISTS idx_trade_proposals_session
  ON trade_proposals(session_date_et, status);

CREATE TABLE IF NOT EXISTS ai_explanation_cache (
  id INTEGER PRIMARY KEY,
  cache_key TEXT NOT NULL UNIQUE,
  ticker TEXT NOT NULL,
  session_date_et TEXT NOT NULL,
  headline_hash TEXT NOT NULL,
  model_version TEXT NOT NULL,
  explanation TEXT NOT NULL,
  explanation_short TEXT NOT NULL,
  ai_confidence REAL NOT NULL DEFAULT 0,
  news_sentiment REAL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_cache_session
  ON ai_explanation_cache(session_date_et, model_version);
"""

MIGRATION_SQL = """
-- Phase 7 watchlist columns (idempotent via try/ignore in Python)
"""


def _apply_migrations(conn: sqlite3.Connection) -> None:
    all_tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if "news_headlines" not in all_tables:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS news_headlines (
              id INTEGER PRIMARY KEY,
              ticker TEXT NOT NULL,
              headline_hash TEXT NOT NULL,
              published_at TEXT NOT NULL,
              headline TEXT NOT NULL,
              summary TEXT,
              source TEXT,
              url TEXT,
              ingested_at TEXT NOT NULL,
              UNIQUE(ticker, headline_hash)
            );
            CREATE INDEX IF NOT EXISTS idx_news_ticker_time
              ON news_headlines(ticker, published_at);
            """
        )
    if "trade_proposals" not in all_tables:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS trade_proposals (
              id INTEGER PRIMARY KEY,
              proposal_uuid TEXT NOT NULL UNIQUE,
              strategy_version TEXT NOT NULL,
              model_version TEXT NOT NULL,
              created_at TEXT NOT NULL,
              valid_until TEXT,
              session_date_et TEXT NOT NULL,
              ticker TEXT NOT NULL,
              direction TEXT NOT NULL DEFAULT 'long',
              opportunity_score REAL NOT NULL,
              factor_scores_json TEXT NOT NULL,
              plan_json TEXT NOT NULL,
              risk_verdict TEXT NOT NULL,
              risk_checks_json TEXT NOT NULL,
              risk_rejection_reason TEXT,
              human_verdict TEXT,
              human_rejection_reason TEXT,
              human_approved_at TEXT,
              explanation TEXT,
              explanation_short TEXT,
              status TEXT NOT NULL,
              journal_buy_id INTEGER,
              journal_sell_id INTEGER,
              outcome_net_pnl REAL,
              outcome_exit_reason TEXT,
              FOREIGN KEY (journal_buy_id) REFERENCES trade_journal(id),
              FOREIGN KEY (journal_sell_id) REFERENCES trade_journal(id)
            );
            CREATE INDEX IF NOT EXISTS idx_trade_proposals_session
              ON trade_proposals(session_date_et, status);
            """
        )
    if "ai_explanation_cache" not in all_tables:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ai_explanation_cache (
              id INTEGER PRIMARY KEY,
              cache_key TEXT NOT NULL UNIQUE,
              ticker TEXT NOT NULL,
              session_date_et TEXT NOT NULL,
              headline_hash TEXT NOT NULL,
              model_version TEXT NOT NULL,
              explanation TEXT NOT NULL,
              explanation_short TEXT NOT NULL,
              ai_confidence REAL NOT NULL DEFAULT 0,
              news_sentiment REAL,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_ai_cache_session
              ON ai_explanation_cache(session_date_et, model_version);
            """
        )
    if "trade_journal" in all_tables:
        journal_cols = {row[1] for row in conn.execute("PRAGMA table_info(trade_journal)")}
        if "proposal_id" not in journal_cols:
            conn.execute(
                "ALTER TABLE trade_journal ADD COLUMN proposal_id INTEGER "
                "REFERENCES trade_proposals(id)"
            )
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='watchlist'"
        )
    }
    if "watchlist" not in tables:
        return
    cols = {row[1] for row in conn.execute("PRAGMA table_info(watchlist)")}
    if "source" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN source TEXT DEFAULT 'manual'")
    if "added_via" not in cols:
        conn.execute("ALTER TABLE watchlist ADD COLUMN added_via TEXT DEFAULT 'manual'")


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False, timeout=60.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    _apply_migrations(conn)
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or DEFAULT_DB_PATH
    with connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        _apply_migrations(conn)
        conn.commit()
    return path


def upsert_watchlist(conn: sqlite3.Connection, tickers: list[str]) -> None:
    from investment_agent.watchlist import upsert_tickers

    upsert_tickers(conn, tickers, source="ingest", added_via="run_ingest")


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


def get_max_ohlcv_date(conn: sqlite3.Connection, ticker: str) -> str | None:
    row = conn.execute(
        "SELECT MAX(date) AS d FROM ohlcv_daily WHERE ticker = ?",
        (ticker.upper(),),
    ).fetchone()
    return row["d"] if row and row["d"] else None


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


def get_active_watchlist(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT ticker FROM watchlist WHERE active = 1 ORDER BY ticker"
    ).fetchall()
    return [row["ticker"] for row in rows]


def get_ohlcv_bars(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
) -> list[sqlite3.Row]:
    """Daily OHLCV rows for a ticker, sorted ascending by date."""
    clauses = ["ticker = ?"]
    params: list[Any] = [ticker.upper()]
    if start_date:
        clauses.append("date >= ?")
        params.append(start_date)
    if end_date:
        clauses.append("date <= ?")
        params.append(end_date)
    sql = f"""
        SELECT ticker, date, open, high, low, close, volume, source
        FROM ohlcv_daily
        WHERE {' AND '.join(clauses)}
        ORDER BY date ASC
    """
    if limit is not None:
        sql = f"""
            SELECT * FROM (
                SELECT ticker, date, open, high, low, close, volume, source
                FROM ohlcv_daily
                WHERE {' AND '.join(clauses)}
                ORDER BY date DESC
                LIMIT ?
            ) sub ORDER BY date ASC
        """
        params.append(limit)
    return conn.execute(sql, params).fetchall()


def get_ohlcv_coverage(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT ticker,
               MIN(date) AS first_date,
               MAX(date) AS last_date,
               COUNT(*) AS bar_count
        FROM ohlcv_daily
        GROUP BY ticker
        ORDER BY ticker
        """
    ).fetchall()
    return [dict(row) for row in rows]


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


def insert_news_headline(conn: sqlite3.Connection, row: dict[str, Any]) -> bool:
    """Insert headline if new; return True when a row was inserted."""
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO news_headlines
          (ticker, headline_hash, published_at, headline, summary, source, url, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["ticker"].upper(),
            row["headline_hash"],
            row["published_at"],
            row["headline"],
            row.get("summary"),
            row.get("source"),
            row.get("url"),
            row["ingested_at"],
        ),
    )
    return cur.rowcount > 0


def list_news_headlines(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    since_iso: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    sym = ticker.upper()
    if since_iso:
        rows = conn.execute(
            """
            SELECT ticker, headline_hash, published_at, headline, summary, source, url, ingested_at
            FROM news_headlines
            WHERE ticker = ? AND published_at >= ?
            ORDER BY published_at DESC
            LIMIT ?
            """,
            (sym, since_iso, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT ticker, headline_hash, published_at, headline, summary, source, url, ingested_at
            FROM news_headlines
            WHERE ticker = ?
            ORDER BY published_at DESC
            LIMIT ?
            """,
            (sym, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def purge_news_older_than(conn: sqlite3.Connection, cutoff_iso: str) -> int:
    cur = conn.execute(
        "DELETE FROM news_headlines WHERE published_at < ?",
        (cutoff_iso,),
    )
    return int(cur.rowcount)
