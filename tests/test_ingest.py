"""Tests for ingest orchestration and incremental refresh logic."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.config import Settings
from investment_agent.db import init_db, insert_quote, insert_ticker_metrics
from investment_agent.db_maintenance import acquire_ingest_lock, release_ingest_lock
from investment_agent.ingest import (
    _needs_bars_refresh,
    _needs_quote_refresh,
    run_ingest,
)
from investment_agent.watchlist import load_preset_into_watchlist, load_preset_tickers


def _recent_iso(hours_ago: float = 1.0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.replace(microsecond=0).isoformat()


def test_load_sp500_preset_has_many_tickers():
    tickers = load_preset_tickers("sp500")
    assert len(tickers) >= 500
    assert "AAPL" in tickers
    assert "SPY" in tickers


def test_load_sp500_preset_into_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sp500.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = load_preset_into_watchlist(conn, "sp500")
        conn.commit()
        assert result["tickers_loaded"] >= 500
        count = conn.execute("SELECT COUNT(*) AS c FROM watchlist WHERE active = 1").fetchone()["c"]
        assert count >= 500
        conn.close()


def test_needs_quote_refresh_skips_fresh_data():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "q.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        insert_quote(
            conn,
            {
                "ticker": "AAPL",
                "captured_at": _recent_iso(1.0),
                "price": 100.0,
                "open": 99.0,
                "high": 101.0,
                "low": 98.0,
                "prev_close": 99.5,
            },
        )
        conn.commit()
        assert _needs_quote_refresh(conn, "AAPL", stale_hours=20.0) is False
        assert _needs_quote_refresh(conn, "MSFT", stale_hours=20.0) is True
        conn.close()


def test_needs_bars_refresh_skips_fresh_metrics():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "b.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": _recent_iso(2.0),
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100,
                "last_quote": 100,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        conn.commit()
        assert _needs_bars_refresh(conn, "AAPL", stale_hours=20.0) is False
        assert _needs_bars_refresh(conn, "NVDA", stale_hours=20.0) is True
        conn.close()


def test_run_ingest_incremental_skips_fresh_symbols():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "inc.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        now = _recent_iso(1.0)
        for ticker in ("AAPL", "MSFT", "NVDA"):
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": now,
                    "price": 100.0,
                    "open": 99.0,
                    "high": 101.0,
                    "low": 98.0,
                    "prev_close": 99.5,
                },
            )
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": 3.0,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": True,
                },
            )
        conn.commit()
        conn.close()

        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="test-fred",
            finnhub_api_key="test-finnhub",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        mock_fh = MagicMock()
        mock_fh.get_quote.return_value = {"c": 100, "o": 99, "h": 101, "l": 98, "pc": 99}

        with (
            patch("investment_agent.ingest.fetch_vix", return_value=("2026-01-01", 15.0)),
            patch("investment_agent.ingest.FinnhubClient", return_value=mock_fh),
            patch("investment_agent.ingest.get_daily_bars", return_value=[]),
        ):
            summary = run_ingest(
                settings,
                db_path=path,
                incremental=True,
                stale_hours=20.0,
            )

        assert summary["incremental"] is True
        assert summary["quotes_skipped"] >= 3
        assert summary["bars_skipped"] >= 3
        assert mock_fh.get_quote.call_count < len(summary["tickers"])


def test_run_ingest_after_close_uses_shorter_quote_stale_window():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ac.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        now = _recent_iso(3.0)  # 3 hours ago — fresh for 20h, stale for 2h quotes
        for ticker in ("AAPL",):
            insert_quote(
                conn,
                {
                    "ticker": ticker,
                    "captured_at": now,
                    "price": 100.0,
                    "open": 99.0,
                    "high": 101.0,
                    "low": 98.0,
                    "prev_close": 99.5,
                },
            )
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": 3.0,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": True,
                },
            )
        conn.commit()
        conn.close()

        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="test-fred",
            finnhub_api_key="test-finnhub",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        mock_fh = MagicMock()
        mock_fh.get_quote.return_value = {"c": 100, "o": 99, "h": 101, "l": 98, "pc": 99}

        with (
            patch("investment_agent.ingest.fetch_vix", return_value=("2026-01-01", 15.0)),
            patch("investment_agent.ingest.FinnhubClient", return_value=mock_fh),
            patch("investment_agent.ingest.get_daily_bars", return_value=[]),
        ):
            summary = run_ingest(
                settings,
                db_path=path,
                incremental=True,
                stale_hours=20.0,
                quote_stale_hours=2.0,
                bar_stale_hours=12.0,
            )

        assert summary["quote_stale_hours"] == 2.0
        assert summary["quotes_refreshed"] >= 1
        assert summary["bars_skipped"] >= 1


def test_run_ingest_returns_error_when_lock_held():
    import investment_agent.db_maintenance as dm

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "lock.db"
        init_db(path)
        lock = Path(tmp) / "ingest.lock"
        dm.INGEST_LOCK_PATH = lock
        acquire_ingest_lock(detail="other")

        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="test-fred",
            finnhub_api_key="test-finnhub",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        summary = run_ingest(settings, db_path=path)
        assert summary["ok"] is False
        assert summary["error_count"] == 1
        assert "Ingest is running" in summary["errors"][0]
        release_ingest_lock()
