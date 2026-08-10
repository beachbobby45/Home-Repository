"""Tests for Step 3 status labels and Special Watch reporting."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.db import init_db, insert_ticker_metrics
from investment_agent.step3_status import (
    LOW_LIQUIDITY,
    MISSING_METRICS,
    STEP3_PASS,
    TOO_QUIET,
    TOO_WILD,
    classify_step3_status,
)
from investment_agent.watchlist import (
    build_special_watch_report,
    load_preset_tickers,
)


def test_classify_step3_status_bands():
    assert classify_step3_status(meets_liquidity=True, near_swing=True, avg_range_pct=3.0) == STEP3_PASS
    assert classify_step3_status(meets_liquidity=True, near_swing=False, avg_range_pct=1.5) == TOO_QUIET
    assert classify_step3_status(meets_liquidity=True, near_swing=False, avg_range_pct=6.0) == TOO_WILD
    assert classify_step3_status(meets_liquidity=False, near_swing=False, avg_range_pct=3.0) == LOW_LIQUIDITY
    assert classify_step3_status(ticker="X") == MISSING_METRICS


def test_datacenter_us_preset_loads():
    tickers = load_preset_tickers("datacenter_us")
    assert len(tickers) >= 90
    assert "VRT" in tickers
    assert "ACM" in tickers
    assert "ASML" in tickers
    assert "NBIS" in tickers
    assert "DRAM" in tickers
    assert len(tickers) == len(set(tickers))


def test_add_special_watch_ticker_manual_extra():
    from investment_agent.watchlist import (
        add_special_watch_ticker,
        get_special_watch_extras,
        merge_special_watch_tickers,
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sw2.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        result = add_special_watch_ticker(conn, "datacenter_us", "TESTX")
        conn.commit()
        assert result["ok"] is True
        assert result["added_to_extras"] is True
        assert get_special_watch_extras(conn, "datacenter_us") == ["TESTX"]

        merged = merge_special_watch_tickers("datacenter_us", ["TESTX"])
        assert "TESTX" in merged
        assert "VRT" in merged

        # Preset ticker does not duplicate in extras
        result2 = add_special_watch_ticker(conn, "datacenter_us", "VRT")
        conn.commit()
        assert result2["already_in_preset"] is True
        assert get_special_watch_extras(conn, "datacenter_us") == ["TESTX"]

        report = build_special_watch_report(conn, "datacenter_us")
        by_ticker = {r["ticker"]: r for r in report["tickers"]}
        assert "TESTX" in by_ticker
        assert by_ticker["TESTX"]["step3_status"] == MISSING_METRICS
        conn.close()


def test_build_special_watch_report_counts():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sw.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        insert_ticker_metrics(
            conn,
            {
                "ticker": "VRT",
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 1_000_000_000.0,
                "avg_range_pct": 3.0,
                "liquidity_cap": 8_000_000.0,
                "last_close": 100.0,
                "last_quote": 100.0,
                "meets_liquidity_min": True,
                "near_swing_target": True,
            },
        )
        insert_ticker_metrics(
            conn,
            {
                "ticker": "FIX",
                "computed_at": "2026-08-01T12:00:00+00:00",
                "adv_dollar": 500_000_000.0,
                "avg_range_pct": 6.0,
                "liquidity_cap": 4_000_000.0,
                "last_close": 50.0,
                "last_quote": 50.0,
                "meets_liquidity_min": True,
                "near_swing_target": False,
            },
        )
        conn.commit()

        report = build_special_watch_report(conn, "datacenter_us")
        conn.close()

        assert report["preset"] == "datacenter_us"
        assert report["ticker_count"] >= 90
        assert report["step3_pass"] >= 1
        assert report["too_wild"] >= 1

        by_ticker = {r["ticker"]: r for r in report["tickers"]}
        assert by_ticker["VRT"]["step3_status"] == STEP3_PASS
        assert by_ticker["FIX"]["step3_status"] == TOO_WILD
        assert by_ticker["VRT"]["step3_label"] == "Step 3 pass"
