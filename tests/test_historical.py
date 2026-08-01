"""Tests for historical analysis and prior-day evaluation."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows, upsert_watchlist
from investment_agent.historical import (
    build_historical_summary,
    evaluate_period,
    evaluate_prior_day,
    evaluate_trading_day,
    open_based_range_pct,
    simulate_intraday_outcome,
)
from investment_agent.learning import generate_learning_report


def _seed_minimal_history(path: Path) -> tuple[str, str]:
    end = datetime.now(timezone.utc)
    eval_date = (end - timedelta(days=1)).strftime("%Y-%m-%d")
    history_start = (end - timedelta(days=10)).strftime("%Y-%m-%d")

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row
        upsert_watchlist(conn, ["AAPL", "SPY"])

        rows = []
        for offset in range(10, 0, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            close = 100.0 + offset * 0.1
            if day == eval_date:
                open_px = close
                high = open_px * 1.012
                low = open_px * 0.996
            else:
                open_px = close * 0.998
                high = open_px * 1.015
                low = open_px * 0.985
            rows.append(
                {
                    "ticker": "AAPL",
                    "date": day,
                    "open": round(open_px, 2),
                    "high": round(high, 2),
                    "low": round(low, 2),
                    "close": round(close, 2),
                    "volume": 10_000_000,
                    "source": "test",
                }
            )
        insert_ohlcv_rows(conn, rows)
        conn.commit()

    return eval_date, history_start


def test_open_based_range_and_simulation():
    assert open_based_range_pct(100, 103, 97) == 6.0
    assert simulate_intraday_outcome(100, 102, 99) == "target"
    assert simulate_intraday_outcome(100, 101, 99.4) == "stop"
    assert simulate_intraday_outcome(100, 100.5, 99.8) == "neither"


def test_evaluate_trading_day_finds_screened_matches():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, _ = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = evaluate_trading_day(conn, eval_date)
        conn.close()
        assert result["tickers_evaluated"] == 1
        assert result["summary"]["screened_count"] >= 1
        match = result["screened_matches"][0]
        assert match["ticker"] == "AAPL"
        assert match["would_screen"] is True


def test_evaluate_prior_day_and_period():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, history_start = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        prior = evaluate_prior_day(conn, reference_date=(datetime.strptime(eval_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))
        assert prior is not None
        assert prior["eval_date"] == eval_date
        period = evaluate_period(conn, history_start, eval_date)
        assert period["days_evaluated"] >= 1
        summary = build_historical_summary(conn)
        assert summary["has_data"] is True
        conn.close()


def test_learning_report_includes_historical_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "hist.db"
        init_db(path)
        eval_date, _ = _seed_minimal_history(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        report = generate_learning_report(conn, report_date=eval_date)
        conn.close()
        assert "prior_day_evaluation" in report
        assert "continual_learning" in report
        assert "today_journal" in report
        assert report["continual_learning"]["lookback_days"] == 30
