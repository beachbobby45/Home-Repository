"""Tests for trading-day period windows in period screener."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.period_screener import (
    build_ranked_candidates,
    list_trading_dates,
    date_range_for_period,
    run_period_screener,
)
from investment_agent.watchlist import load_preset_into_watchlist


def _insert_spy_week(conn: sqlite3.Connection, start: datetime, sessions: int) -> list[str]:
    """Insert SPY bars on weekdays only (no weekends)."""
    dates: list[str] = []
    d = start
    while len(dates) < sessions:
        if d.weekday() < 5:
            ds = d.strftime("%Y-%m-%d")
            insert_ohlcv_rows(
                conn,
                [
                    {
                        "ticker": "SPY",
                        "date": ds,
                        "open": 100.0,
                        "high": 103.0,
                        "low": 99.0,
                        "close": 101.0,
                        "volume": 1_000_000,
                        "source": "test",
                    }
                ],
            )
            dates.append(ds)
        d += timedelta(days=1)
    return dates


def test_list_trading_dates_excludes_weekends():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "td.db"
        init_db(path)
        conn = sqlite3.connect(path)
        end = datetime(2026, 8, 10, tzinfo=timezone.utc)  # Monday
        dates = _insert_spy_week(conn, end - timedelta(days=20), sessions=14)
        conn.commit()
        listed = list_trading_dates(conn, count=14, end_date=end.strftime("%Y-%m-%d"))
        conn.close()
        assert len(listed) == 14
        for ds in listed:
            wd = datetime.strptime(ds, "%Y-%m-%d").weekday()
            assert wd < 5, f"{ds} should be a weekday"
        assert listed[-1] <= end.strftime("%Y-%m-%d")


def test_period_screener_uses_trading_day_window():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "td2.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        end = datetime(2026, 8, 10, tzinfo=timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "SPY", "DIA", "QQQ"], end=end)
        conn.commit()

        trading_dates = list_trading_dates(conn, count=14, end_date=end.strftime("%Y-%m-%d"))
        start, end_str = date_range_for_period(14, end_date=end.strftime("%Y-%m-%d"), conn=conn)
        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end_str,
            trading_dates=trading_dates,
            requested_trading_days=14,
            min_days_screened=1,
        )
        ranked = build_ranked_candidates(conn, period_days=14, end_date=end.strftime("%Y-%m-%d"))
        conn.close()

        assert result["requested_trading_days"] == 14
        assert result["days_evaluated"] <= 14
        assert ranked["trading_days_in_period"] <= 14
        if ranked["ranked"]:
            row = ranked["ranked"][0]
            assert row.get("requested_trading_days") == 14
            assert row["days_screened"] <= 14
