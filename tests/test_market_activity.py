"""Tests for Market Activity Engine (Phase 1B Inc 12)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_macro, insert_ohlcv_rows, insert_regime_snapshot
from investment_agent.market_activity import (
    ABOVE_AVERAGE_MIN,
    band_for_score,
    evaluate_market_activity,
    list_recent_evaluations,
    save_market_activity_evaluation,
    score_market_direction,
    spy_20d_return_pct,
)
from investment_agent.quote_snapshots import upsert_quote_snapshot
from investment_agent.trading_day import build_trading_day_status

ET = ZoneInfo("America/New_York")


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_spy_bars(conn: sqlite3.Connection, *, uptrend: bool = True):
    closes = [100 + i * (0.5 if uptrend else -0.2) for i in range(25)]
    rows = []
    end = datetime.now(timezone.utc)
    for i, close in enumerate(closes):
        day = (end - timedelta(days=len(closes) - i)).strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": "SPY",
                "date": day,
                "open": close * 0.99,
                "high": close * 1.01,
                "low": close * 0.98,
                "close": close,
                "volume": 80_000_000 if i < len(closes) - 1 else 95_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def _seed_index_snapshots(conn: sqlite3.Connection, *, spy_change: float = 0.4):
    for sym, ch in [("SPY", spy_change), ("DIA", 0.2), ("QQQ", 0.3)]:
        base = 100.0
        open_px = base
        price = base * (1 + ch / 100)
        upsert_quote_snapshot(
            conn,
            session_date_et="2026-08-03",
            slot="plus_15m",
            ticker=sym,
            captured_at="2026-08-03T13:50:00+00:00",
            price=price,
            open_px=open_px,
            prev_close=base * 0.99,
        )
    conn.commit()


def test_band_for_score_thresholds():
    assert band_for_score(95).key == "exceptional"
    assert band_for_score(80).key == "above_average"
    assert band_for_score(65).key == "average"
    assert band_for_score(45).key == "below_average"
    assert band_for_score(30).key == "negative"


def test_score_market_direction_positive():
    score = score_market_direction({"SPY": 0.5, "DIA": 0.3, "QQQ": 0.4})
    assert score is not None
    assert score > 50


def test_evaluate_blocks_when_bull_gate_off():
    conn = _conn()
    try:
        _seed_spy_bars(conn, uptrend=False)
        _seed_index_snapshots(conn, spy_change=0.5)
        insert_macro(conn, "VIXCLS", "2026-08-03", 16.0, "2026-08-03T12:00:00+00:00")
        when = datetime(2026, 8, 3, 10, 0, tzinfo=ET)
        result = evaluate_market_activity(conn, when=when, persist=False)
        assert result["allow_trade"] is False
        assert result["bull_gate_ok"] is False
        assert spy_20d_return_pct(conn) is not None
        assert spy_20d_return_pct(conn) < 0
    finally:
        conn.close()


def test_evaluate_allows_strong_day():
    conn = _conn()
    try:
        _seed_spy_bars(conn, uptrend=True)
        _seed_index_snapshots(conn, spy_change=1.2)
        insert_macro(conn, "VIXCLS", "2026-08-03", 14.0, "2026-08-03T12:00:00+00:00")
        when = datetime(2026, 8, 3, 10, 0, tzinfo=ET)
        with patch(
            "investment_agent.market_activity.score_sector_participation",
            return_value=85.0,
        ):
            result = evaluate_market_activity(conn, when=when, persist=False)
        assert result["score"] >= ABOVE_AVERAGE_MIN
        assert result["allow_trade"] is True
        assert result["bull_gate_ok"] is True
    finally:
        conn.close()


def test_flip_detection_two_consecutive_low_scores():
    conn = _conn()
    try:
        _seed_spy_bars(conn, uptrend=True)
        when = datetime(2026, 8, 3, 11, 0, tzinfo=ET)
        save_market_activity_evaluation(
            conn,
            session_date_et="2026-08-03",
            captured_at="2026-08-03T15:00:00+00:00",
            slot="plus_15m",
            score=70,
            band="average",
            allow_trade=False,
            bull_gate_ok=True,
            exit_alert=False,
            components={},
            summary="first low read",
        )
        conn.commit()
        with patch(
            "investment_agent.market_activity.score_market_direction",
            return_value=55.0,
        ), patch(
            "investment_agent.market_activity.score_index_momentum",
            return_value=50.0,
        ), patch(
            "investment_agent.market_activity.score_sector_participation",
            return_value=50.0,
        ):
            result = evaluate_market_activity(conn, when=when, persist=False)
        assert result["score"] < ABOVE_AVERAGE_MIN
        assert result["exit_alert"] is True
    finally:
        conn.close()


def test_persist_evaluation():
    conn = _conn()
    try:
        _seed_spy_bars(conn, uptrend=True)
        _seed_index_snapshots(conn)
        insert_macro(conn, "VIXCLS", "2026-08-03", 16.0, "2026-08-03T12:00:00+00:00")
        when = datetime(2026, 8, 3, 10, 0, tzinfo=ET)
        evaluate_market_activity(conn, when=when, persist=True)
        conn.commit()
        recent = list_recent_evaluations(conn, "2026-08-03", limit=1)
        assert len(recent) == 1
        assert recent[0]["score"] >= 0
    finally:
        conn.close()


def test_build_trading_day_status_includes_market_activity():
    conn = _conn()
    try:
        _seed_spy_bars(conn, uptrend=True)
        _seed_index_snapshots(conn)
        insert_macro(conn, "VIXCLS", "2026-08-03", 16.0, "2026-08-03T12:00:00+00:00")
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": 0.4,
                "dia_change_pct": 0.2,
                "qqq_change_pct": 0.3,
                "all_indices_down": 0,
                "block_new_longs": 0,
                "summary": "Regime OK",
            },
        )
        conn.commit()
        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert "market_activity" in status
        assert "score" in status["market_activity"]
        assert "band" in status["market_activity"]
    finally:
        conn.close()
