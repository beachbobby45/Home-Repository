"""Deterministic demo/test dataset for dashboard verification."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from investment_agent.db import (
    init_db,
    insert_macro,
    insert_quote,
    insert_regime_snapshot,
    insert_ticker_metrics,
    upsert_watchlist,
)
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import insert_trade
from investment_agent.strategy import STOP_PCT, TARGET_PCT

NOW = datetime.now(timezone.utc).replace(microsecond=0)
NOW_ISO = NOW.isoformat()
MONTH_KEY = NOW.strftime("%Y-%m")
TRADE_TIME = NOW.replace(hour=14, minute=30).isoformat()


def _target(entry: float) -> float:
    return round(entry * (1 + TARGET_PCT / 100), 2)


def _stop(entry: float) -> float:
    return round(entry * (1 - STOP_PCT / 100), 2)


def seed_demo_db(db_path: Path | None = None) -> Path:
    """Populate a database with realistic test data covering every dashboard section.

    Scenario:
    - Regime OK, VIX 18.25
    - Completed AAPL round trip (+profit) this month
    - Open NVDA in_trade at +1.13% target (quote at target)
    - MSFT armed, META alert (approaching stop)
    - Queue + journal + metrics for screener
    """
    path = init_db(db_path)

    tickers = ["SPY", "DIA", "QQQ", "AAPL", "MSFT", "NVDA", "AMD", "META", "TSLA", "IWM"]

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row

        # Clear mutable demo tables for idempotent re-seed
        for table in (
            "price_alerts",
            "trade_journal",
            "queue_items",
            "sweep_history",
            "jar_balances",
            "app_settings",
            "quotes",
            "ticker_metrics",
            "macro_snapshots",
            "regime_snapshots",
            "ingest_log",
        ):
            conn.execute(f"DELETE FROM {table}")

        upsert_watchlist(conn, tickers)

        insert_macro(conn, "VIXCLS", NOW.strftime("%Y-%m-%d"), 18.25, NOW_ISO)
        insert_regime_snapshot(
            conn,
            {
                "captured_at": NOW_ISO,
                "spy_change_pct": 0.35,
                "dia_change_pct": 0.12,
                "qqq_change_pct": -0.18,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK — SPY +0.35%, DIA +0.12%, QQQ -0.18%",
            },
        )

        metrics_rows = [
            ("AAPL", 100.0, 3.1),
            ("MSFT", 420.0, 2.9),
            ("NVDA", 100.0, 3.0),
            ("META", 500.0, 3.2),
            ("AMD", 160.0, 3.0),
            ("TSLA", 250.0, 4.1),
            ("SPY", 745.0, 1.2),
            ("DIA", 440.0, 1.0),
            ("QQQ", 480.0, 1.5),
            ("IWM", 220.0, 2.0),
        ]
        for ticker, price, avg_range in metrics_rows:
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": NOW_ISO,
                    "adv_dollar": 80_000_000,
                    "avg_range_pct": avg_range,
                    "liquidity_cap": 640_000,
                    "last_close": price,
                    "last_quote": price,
                    "meets_liquidity_min": ticker not in ("SPY", "DIA", "QQQ"),
                    "near_swing_target": avg_range >= 2.0 and avg_range <= 4.0,
                },
            )

        # Quotes — NVDA at target, META near stop, MSFT mid-range
        quote_prices = {
            "SPY": 745.0,
            "DIA": 440.0,
            "QQQ": 480.0,
            "AAPL": 101.5,
            "MSFT": 420.0,
            "NVDA": _target(100.0) + 0.05,  # above target
            "META": _stop(500.0) + 1.0,  # above stop but close
            "AMD": 160.0,
            "TSLA": 250.0,
            "IWM": 220.0,
        }
        for ticker, price in quote_prices.items():
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": NOW_ISO,
                    "price": price,
                    "open": price * 0.998,
                    "high": price * 1.005,
                    "low": price * 0.995,
                    "prev_close": price * 0.99,
                },
            )

        # Queue items in multiple states
        queue_specs = [
            # closed winner (already traded)
            (
                "AAPL",
                "closed",
                100.0,
                10_000,
                "Completed round trip — journal below.",
            ),
            # in_trade — NVDA at target
            (
                "NVDA",
                "in_trade",
                100.0,
                10_000,
                "Demo in-trade position — monitor should fire TARGET_HIT.",
            ),
            ("MSFT", "armed", 420.0, 10_000, "Armed — waiting for entry trigger."),
            ("META", "alert", 500.0, 10_000, "Alert state — price near stop."),
            ("AMD", "watching", 160.0, 10_000, "Watching — screener candidate."),
        ]

        queue_ids: dict[str, int] = {}
        for ticker, state, entry, size, thesis in queue_specs:
            cur = conn.execute(
                """
                INSERT INTO queue_items
                  (ticker, state, suggested_size, entry_price, target_price, stop_price,
                   avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 3.0, 640000, ?, ?, ?)
                """,
                (
                    ticker,
                    state,
                    size,
                    entry,
                    _target(entry),
                    _stop(entry),
                    thesis,
                    NOW_ISO,
                    NOW_ISO,
                ),
            )
            queue_ids[ticker] = int(cur.lastrowid)

        # Journal — AAPL round trip (profit), NVDA open buy
        insert_trade(
            conn,
            ticker="AAPL",
            side="BUY",
            shares=10,
            price=100.0,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo buy",
            queue_id=queue_ids["AAPL"],
        )
        insert_trade(
            conn,
            ticker="AAPL",
            side="SELL",
            shares=10,
            price=101.13,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo sell at target",
            queue_id=queue_ids["AAPL"],
        )
        insert_trade(
            conn,
            ticker="NVDA",
            side="BUY",
            shares=50,
            price=100.0,
            fee=7.0,
            executed_at=TRADE_TIME,
            notes="Demo NVDA entry",
            queue_id=queue_ids["NVDA"],
        )

        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES ('tax_reserve_rate', '0.25')"
        )

        conn.commit()

    return path


def expected_demo_summary() -> dict:
    """Known values after seed — used by verification tests."""
    # AAPL: gross 11.3 - fees 14 = -2.7
    aapl_pnl = (101.13 - 100.0) * 10 - 14.0
    # Cash: 10000 - 1007 (AAPL buy) + 1004.3 (AAPL sell) - 5007 (NVDA buy) = 4990.3
    nvda_cost = 50 * 100 + 7
    cash = ORIGINAL_BASIS - (10 * 100 + 7) + (10 * 101.13 - 7) - nvda_cost
    return {
        "month_key": MONTH_KEY,
        "monthly_realized_net": aapl_pnl,
        "tradable_cash": cash,
        "queue_count": 5,
        "journal_count": 3,
        "regime_ok": True,
        "vix": 18.25,
    }
