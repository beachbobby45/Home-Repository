"""Deterministic demo/test dataset for dashboard verification."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from investment_agent.db import (
    init_db,
    insert_macro,
    insert_news_headline,
    insert_ohlcv_rows,
    insert_quote,
    insert_regime_snapshot,
    insert_ticker_metrics,
    upsert_watchlist,
)
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.journal import insert_trade
from investment_agent.news_service import headline_hash
from investment_agent.strategy import STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")

NOW = datetime.now(timezone.utc).replace(microsecond=0)
NOW_ISO = NOW.isoformat()
MONTH_KEY = NOW.strftime("%Y-%m")
TRADE_TIME = NOW.replace(hour=14, minute=30).isoformat()


def _target(entry: float) -> float:
    return round(entry * (1 + TARGET_PCT / 100), 2)


def _stop(entry: float) -> float:
    return round(entry * (1 - STOP_PCT / 100), 2)


def _seed_ohlcv_history(conn: sqlite3.Connection, tickers: list[str], end: datetime) -> None:
    """~25 trading days of synthetic daily bars ending the day before `end`."""
    tradeables = [t for t in tickers if t not in ("SPY", "DIA", "QQQ")]
    base_prices = {
        "AAPL": 100.0,
        "MSFT": 420.0,
        "NVDA": 100.0,
        "META": 500.0,
        "AMD": 160.0,
        "TSLA": 250.0,
        "IWM": 220.0,
    }
    prior_day = (end - timedelta(days=1)).strftime("%Y-%m-%d")

    for ticker in tickers:
        base = base_prices.get(ticker, 100.0)
        rows: list[dict] = []
        for offset in range(25, 0, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            close = base * (1 + 0.002 * ((25 - offset) % 5 - 2))
            if ticker in tradeables and day == prior_day:
                open_px = close
                high = open_px * 1.018
                low = open_px * 0.992
            elif ticker in tradeables:
                open_px = close * 0.998
                swing = 0.025 if ticker in ("AAPL", "NVDA", "AMD", "META") else 0.015
                high = open_px * (1 + swing / 2)
                low = open_px * (1 - swing / 2)
            else:
                open_px = close * 0.999
                high = close * 1.004
                low = close * 0.996
            rows.append(
                {
                    "ticker": ticker,
                    "date": day,
                    "open": round(open_px, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": 5_000_000,
                    "source": "demo",
                }
            )
        insert_ohlcv_rows(conn, rows)


def _seed_demo_proposals(conn: sqlite3.Connection) -> None:
    """Sample trade proposals for Phase 1 dashboard + learning v2 demos."""
    session = datetime.now(ET).strftime("%Y-%m-%d")
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    valid = (
        datetime.now(ET).replace(hour=11, minute=30, second=0, microsecond=0)
        .astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
    base_plan = {
        "limit_buy_price": 100.0,
        "limit_sell_price": 101.5,
        "stop_price": 99.25,
        "shares": 100,
        "net_at_target": 150.0,
        "expected_rr": 2.0,
        "max_risk_dollars": 75.0,
        "entry_mode": "pullback_limit",
    }
    specs = [
        {
            "ticker": "AAPL",
            "score": 84.0,
            "status": "closed",
            "risk_verdict": "approved",
            "human_verdict": "approved",
            "outcome_net_pnl": 120.0,
            "model_version": "rule-based-v1",
            "factors": {
                "market_regime": 80,
                "technical_setup": 85,
                "momentum": 78,
                "news_sentiment": 72,
                "risk_reward": 88,
                "dollar_history": 70,
            },
            "explanation_short": "AAPL — score 84 · sentiment 72 · limit $100.00",
        },
        {
            "ticker": "NVDA",
            "score": 79.0,
            "status": "proposed",
            "risk_verdict": "approved",
            "human_verdict": None,
            "outcome_net_pnl": None,
            "model_version": "rule-based-v1",
            "factors": {
                "market_regime": 80,
                "technical_setup": 75,
                "momentum": 82,
                "news_sentiment": 55,
                "risk_reward": 80,
            },
            "explanation_short": "NVDA — score 79 · sentiment 55 · limit $100.00",
        },
        {
            "ticker": "META",
            "score": 76.0,
            "status": "human_rejected",
            "risk_verdict": "approved",
            "human_verdict": "rejected",
            "human_rejection_reason": "NEWS_RISK: News/event too risky",
            "outcome_net_pnl": None,
            "model_version": "rule-based-v1",
            "factors": {"market_regime": 75, "news_sentiment": 38, "risk_reward": 76},
            "explanation_short": "META — score 76 · sentiment 38 · limit $100.00",
        },
    ]
    for spec in specs:
        conn.execute(
            """
            INSERT INTO trade_proposals (
              proposal_uuid, strategy_version, model_version, created_at, valid_until,
              session_date_et, ticker, direction, opportunity_score, factor_scores_json,
              plan_json, risk_verdict, risk_checks_json, risk_rejection_reason,
              human_verdict, human_rejection_reason, human_approved_at,
              explanation, explanation_short, status,
              journal_buy_id, journal_sell_id, outcome_net_pnl, outcome_exit_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'long', ?, ?, ?, ?, '[]', NULL, ?, ?, NULL, ?, ?, ?, NULL, NULL, ?, NULL)
            """,
            (
                str(uuid.uuid4()),
                "phase1-capital-builder-v1",
                spec["model_version"],
                created,
                valid,
                session,
                spec["ticker"],
                spec["score"],
                json.dumps(spec["factors"]),
                json.dumps({**base_plan, "ticker": spec["ticker"]}),
                spec["risk_verdict"],
                spec.get("human_verdict"),
                spec.get("human_rejection_reason"),
                f"Demo explanation for {spec['ticker']}.",
                spec["explanation_short"],
                spec["status"],
                spec.get("outcome_net_pnl"),
            ),
        )

    insert_news_headline(
        conn,
        {
            "ticker": "NVDA",
            "headline_hash": headline_hash("NVDA beats revenue estimates"),
            "published_at": created,
            "headline": "NVDA beats revenue estimates with strong data-center growth",
            "summary": "Demo headline",
            "source": "demo",
            "url": None,
            "ingested_at": created,
        },
    )


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
            "ai_explanation_cache",
            "trade_proposals",
            "news_headlines",
            "learning_reports",
            "price_alerts",
            "trade_journal",
            "queue_items",
            "sweep_history",
            "jar_balances",
            "app_settings",
            "quotes",
            "ticker_metrics",
            "ohlcv_daily",
            "macro_snapshots",
            "regime_snapshots",
            "ingest_log",
        ):
            conn.execute(f"DELETE FROM {table}")

        upsert_watchlist(conn, tickers)
        _seed_ohlcv_history(conn, tickers, end=NOW)

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

        # Journal — multi-month history for scenario visualizer + current month
        # June 2026: strong MSFT round trip
        insert_trade(
            conn,
            ticker="MSFT",
            side="BUY",
            shares=10,
            price=400.0,
            fee=7.0,
            executed_at="2026-06-15T14:00:00+00:00",
            notes="Demo Jun buy",
        )
        insert_trade(
            conn,
            ticker="MSFT",
            side="SELL",
            shares=10,
            price=404.52,
            fee=7.0,
            executed_at="2026-06-15T15:00:00+00:00",
            notes="Demo Jun sell at +1.13%",
        )
        # July 2026: smaller AMD round trip
        insert_trade(
            conn,
            ticker="AMD",
            side="BUY",
            shares=20,
            price=150.0,
            fee=7.0,
            executed_at="2026-07-20T14:00:00+00:00",
            notes="Demo Jul buy",
        )
        insert_trade(
            conn,
            ticker="AMD",
            side="SELL",
            shares=20,
            price=151.70,
            fee=7.0,
            executed_at="2026-07-20T15:00:00+00:00",
            notes="Demo Jul sell",
        )
        # August 2026: AAPL round trip + NVDA open
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

        _seed_demo_proposals(conn)

        conn.commit()

    return path


def expected_demo_summary() -> dict:
    """Known values after seed — used by verification tests."""
    # AAPL: gross 11.3 - fees 14 = -2.7
    aapl_pnl = (101.13 - 100.0) * 10 - 14.0
    # Cash: 10000 - 1007 (AAPL buy) + 1004.3 (AAPL sell) - 5007 (NVDA buy) = 4990.3
    nvda_cost = 50 * 100 + 7
    msft_jun = (10 * 400 + 7) - (10 * 404.52 - 7)
    amd_jul = (20 * 150 + 7) - (20 * 151.70 - 7)
    cash = (
        ORIGINAL_BASIS
        - msft_jun
        - amd_jul
        - (10 * 100 + 7)
        + (10 * 101.13 - 7)
        - nvda_cost
    )
    # After Jun+Jul round trips (before Aug): MSFT net ~31.2, AMD net ~20.0
    jun_net = (404.52 - 400.0) * 10 - 14.0
    jul_net = (151.70 - 150.0) * 20 - 14.0
    return {
        "month_key": MONTH_KEY,
        "monthly_realized_net": aapl_pnl,
        "tradable_cash": cash,
        "queue_count": 5,
        "journal_count": 7,
        "regime_ok": True,
        "vix": 18.25,
        "timeline_months": 4,  # start + Jun + Jul + Aug
        "jun_realized_net": jun_net,
        "jul_realized_net": jul_net,
    }
