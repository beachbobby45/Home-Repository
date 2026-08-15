"""Tests for Candidate Confirmation Engine (Phase 1B Inc 13)."""

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

from investment_agent.confirmation import (
    CONFIRMATION_PASS_MIN,
    evaluate_ticker_confirmation,
    rank_eligible,
    save_confirmation_evaluation,
)
from investment_agent.db import init_db, insert_ohlcv_rows
from investment_agent.quote_snapshots import upsert_quote_snapshot
from investment_agent.trading_day import build_trading_day_status, resolve_actionable_pick

ET = ZoneInfo("America/New_York")


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_bars(conn: sqlite3.Connection, ticker: str, *, closes: list[float]):
    rows = []
    end = datetime.now(timezone.utc)
    for i, close in enumerate(closes):
        day = (end - timedelta(days=len(closes) - i)).strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": ticker,
                "date": day,
                "open": close * 0.99,
                "high": close * 1.02,
                "low": close * 0.98,
                "close": close,
                "volume": 5_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def _seed_quotes(conn: sqlite3.Connection, ticker: str, *, price: float, open_px: float):
    upsert_quote_snapshot(
        conn,
        session_date_et="2026-08-03",
        slot="plus_15m",
        ticker=ticker,
        captured_at="2026-08-03T13:50:00+00:00",
        price=price,
        open_px=open_px,
        high=price * 1.01,
        low=open_px * 0.995,
        prev_close=open_px * 0.99,
    )
    conn.commit()


def test_rank_eligible_rules():
    assert rank_eligible(0, "above_average") is True
    assert rank_eligible(1, "above_average") is False
    assert rank_eligible(2, "exceptional") is True
    assert rank_eligible(3, "exceptional") is False


def test_confirmation_blocked_when_day_no_trade():
    conn = _conn()
    try:
        market_activity = {"allow_trade": False, "band": "average", "band_label": "Average"}
        result = evaluate_ticker_confirmation(
            conn,
            "AAPL",
            market_activity=market_activity,
            candidate_row={"live_pass_today": True},
        )
        assert result["passes"] is False
        assert result["blocked_by_day"] is True
    finally:
        conn.close()


def test_confirmation_passes_with_strong_scores():
    conn = _conn()
    try:
        _seed_bars(conn, "AAPL", closes=[100 + i for i in range(25)])
        _seed_bars(conn, "SPY", closes=[400 + i for i in range(25)])
        _seed_quotes(conn, "AAPL", price=102.0, open_px=100.0)
        _seed_quotes(conn, "SPY", price=401.0, open_px=400.0)
        market_activity = {"allow_trade": True, "band": "above_average", "band_label": "Above average"}
        with patch(
            "investment_agent.confirmation.score_volume",
            return_value=85.0,
        ), patch(
            "investment_agent.confirmation.score_news_significance",
            return_value=80.0,
        ):
            result = evaluate_ticker_confirmation(
                conn,
                "AAPL",
                market_activity=market_activity,
                candidate_row={"live_pass_today": True, "avg_range_pct": 1.5},
            )
        assert result["score"] >= CONFIRMATION_PASS_MIN
        assert result["passes"] is True
    finally:
        conn.close()


def test_resolve_actionable_pick_requires_confirmation():
    conn = _conn()
    try:
        quotes = {
            "AAPL": {"price": 100.0, "open": 99.0, "high": 101.0, "low": 98.5, "prev_close": 98.0},
        }

        def allow_aapl(ticker: str, rank_index: int) -> bool:
            return ticker == "AAPL" and rank_index == 0

        with patch(
            "investment_agent.trading_day._live_ranked_candidates",
            return_value=[{"ticker": "AAPL", "live_pass_today": True, "dollar_hit_rate_pct": 80}],
        ), patch(
            "investment_agent.trading_day._assess_pick_tradability",
            return_value=(
                {"limit_buy_price": 99.0, "target_price": 101.0},
                {"verdict": "TRADABLE", "detail": "ok"},
                {},
            ),
        ):
            pick, skipped = resolve_actionable_pick(
                conn,
                quotes=quotes,
                deploy=10000,
                net_target=150,
                confirmation_filter=allow_aapl,
            )
        assert pick is not None
        assert pick["ticker"] == "AAPL"

        def block_all(_ticker: str, _idx: int) -> bool:
            return False

        with patch(
            "investment_agent.trading_day._live_ranked_candidates",
            return_value=[{"ticker": "AAPL", "live_pass_today": True, "dollar_hit_rate_pct": 80}],
        ):
            pick2, skipped2 = resolve_actionable_pick(
                conn,
                quotes=quotes,
                deploy=10000,
                net_target=150,
                confirmation_filter=block_all,
            )
        assert pick2 is None
        assert any(s.get("verdict") == "NOT_CONFIRMED" for s in skipped2)
    finally:
        conn.close()


def test_persist_confirmation_evaluation():
    conn = _conn()
    try:
        save_confirmation_evaluation(
            conn,
            session_date_et="2026-08-03",
            captured_at="2026-08-03T15:00:00+00:00",
            ticker="NVDA",
            rank=1,
            score=88,
            passes=True,
            blocked_by_day=False,
            components={"price_momentum": 80.0},
            summary="NVDA 88/100 — PASS",
        )
        conn.commit()
        row = conn.execute(
            "SELECT ticker, score, passes FROM confirmation_evaluations"
        ).fetchone()
        assert row["ticker"] == "NVDA"
        assert row["score"] == 88
        assert row["passes"] == 1
    finally:
        conn.close()


def test_build_trading_day_status_includes_confirmations():
    conn = _conn()
    try:
        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert "confirmations" in status
        assert isinstance(status["confirmations"], list)
    finally:
        conn.close()
