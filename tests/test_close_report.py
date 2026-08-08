"""Tests for Daily Close / Weekly Close reports."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.close_report import (
    generate_daily_close_report,
    generate_weekly_close_report,
    price_at_10_et_from_day_bars,
    save_close_report,
    save_rank_snapshot,
)
from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics, upsert_watchlist


def _seed(conn, eval_date: str):
    upsert_watchlist(conn, ["AAPL", "MSFT"])
    for ticker in ("AAPL", "MSFT"):
        insert_ticker_metrics(
            conn,
            {
                "ticker": ticker,
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 50_000_000,
                "avg_range_pct": 3.0,
                "liquidity_cap": 400_000,
                "last_close": 100.0,
                "last_quote": 100.0,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )

    end = datetime.strptime(eval_date, "%Y-%m-%d")
    rows = []
    for ticker in ("AAPL", "MSFT"):
        for offset in range(10, -1, -1):
            day = (end - timedelta(days=offset)).strftime("%Y-%m-%d")
            open_px = 100.0
            high = round(open_px * (1.015 if day == eval_date and ticker == "AAPL" else 1.012), 2)
            low = round(open_px * 0.988, 2)
            rows.append(
                {
                    "ticker": ticker,
                    "date": day,
                    "open": open_px,
                    "high": round(high, 2),
                    "low": round(open_px * 0.995, 2),
                    "close": round(open_px * 1.005, 2),
                    "volume": 10_000_000,
                    "source": "test",
                }
            )
    insert_ohlcv_rows(conn, rows)


def test_price_at_10_et_bar_index():
    bars = [{"open": 100 + i * 0.1, "ts": f"2026-08-07T{9 + i // 12}:{i % 12}:00"} for i in range(10)]
    assert price_at_10_et_from_day_bars(bars) == bars[6]["open"]


def test_daily_close_report_tabs():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()

        report = generate_daily_close_report(conn, eval_date, fetch_10_et=False)
        assert report["report_type"] == "daily"
        assert "tabs" in report
        assert "step3_pass" in report["tabs"]
        assert "full_top20" in report["tabs"]
        full = report["tabs"]["full_top20"]["rows"]
        assert len(full) >= 1
        aapl = next(r for r in full if r["ticker"] == "AAPL")
        assert aapl["open_entry"]["net_at_high"] > 0
        assert "journal" in report

        save_close_report(conn, report)
        conn.commit()
        conn.close()


def test_weekly_close_report():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        eval_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        _seed(conn, eval_date)
        conn.commit()

        report = generate_weekly_close_report(conn, eval_date, fetch_10_et=False)
        assert report["report_type"] == "weekly"
        assert "summary" in report
        assert report["summary"]["days"] >= 1
        conn.close()


def test_rank_snapshot_saved():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "close.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        save_rank_snapshot(conn, "2026-08-07", [{"ticker": "AAPL", "score": 0.9}])
        conn.commit()
        row = conn.execute("SELECT ranked_json FROM rank_snapshots WHERE snapshot_date = '2026-08-07'").fetchone()
        assert row is not None
        conn.close()
