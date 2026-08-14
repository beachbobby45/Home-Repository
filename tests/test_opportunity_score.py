"""Tests for Phase 1 Opportunity Score (Increment 3)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_news_headline, insert_ohlcv_rows, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.news_service import headline_hash
from investment_agent.opportunity_score import (
    OPPORTUNITY_FLOOR,
    PHASE1_OPPORTUNITY_WEIGHTS,
    composite_opportunity_score,
    compute_opportunity_score,
    passes_opportunity_floor,
    score_dollar_history,
    score_market_regime,
    score_momentum,
    score_relative_strength,
    score_technical_setup,
    score_volatility,
    score_volume,
)
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.watchlist import load_preset_into_watchlist


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _seed_bars(conn, ticker: str, *, closes: list[float], volumes: list[int] | None = None):
    rows = []
    end = datetime.now(timezone.utc)
    vols = volumes or [1_000_000] * len(closes)
    for i, close in enumerate(closes):
        day = (end - timedelta(days=len(closes) - i)).strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": ticker,
                "date": day,
                "open": close * 0.99,
                "high": close * 1.01,
                "low": close * 0.98,
                "close": close,
                "volume": vols[i],
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def test_phase1_weights_include_redistributed_sentiment():
    assert PHASE1_OPPORTUNITY_WEIGHTS["technical_setup"] == 21.0
    assert PHASE1_OPPORTUNITY_WEIGHTS["dollar_history"] == 16.0
    assert sum(PHASE1_OPPORTUNITY_WEIGHTS.values()) == 98.0


def test_composite_renormalizes_missing_factors():
    scores = {
        "market_regime": 80.0,
        "technical_setup": 70.0,
        "momentum": None,
        "relative_strength": None,
        "volume": 60.0,
        "volatility": 75.0,
        "news_significance": None,
        "earnings_events": 35.0,
        "dollar_history": 90.0,
    }
    composite, used = composite_opportunity_score(scores)
    assert composite > 0
    assert "momentum" not in used
    assert "market_regime" in used
    expected = round(
        sum(PHASE1_OPPORTUNITY_WEIGHTS[k] * scores[k] for k in used)
        / sum(PHASE1_OPPORTUNITY_WEIGHTS[k] for k in used)
    )
    assert composite == expected


def test_passes_opportunity_floor():
    assert passes_opportunity_floor(65)
    assert passes_opportunity_floor(80)
    assert not passes_opportunity_floor(64)
    assert not passes_opportunity_floor(None)


def test_score_market_regime_blocks_on_bad_regime():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-14T12:00:00+00:00",
                "spy_change_pct": -0.8,
                "dia_change_pct": -0.4,
                "qqq_change_pct": -0.2,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        conn.commit()
        assert score_market_regime(conn) == 0.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_score_market_regime_positive_when_ok():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-14T12:00:00+00:00",
                "spy_change_pct": 0.6,
                "dia_change_pct": 0.4,
                "qqq_change_pct": 0.8,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "OK",
            },
        )
        conn.commit()
        assert score_market_regime(conn) is not None
        assert score_market_regime(conn) > 50
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_score_technical_setup_live_pass_scores_higher():
    strong = score_technical_setup(
        live_pass=True,
        near_swing=True,
        meets_liquidity=True,
        adv_dollar=20_000_000,
        days_screened=10,
        period_days=14,
    )
    weak = score_technical_setup(
        live_pass=False,
        near_swing=False,
        meets_liquidity=False,
        adv_dollar=0,
        days_screened=0,
        period_days=14,
    )
    assert strong > weak
    assert strong >= 60


def test_score_volatility_prefers_swing_target_band():
    on_target = score_volatility(3.0)
    off_target = score_volatility(8.0)
    assert on_target > off_target


def test_score_momentum_outperformer_scores_high():
    conn, path = _conn()
    try:
        spy_closes = [100 + i * 0.1 for i in range(22)]
        nvda_closes = [100 + i * 0.8 for i in range(22)]
        _seed_bars(conn, "SPY", closes=spy_closes)
        _seed_bars(conn, "NVDA", closes=nvda_closes)
        conn.commit()
        mom = score_momentum(conn, "NVDA")
        assert mom is not None
        assert mom > 55
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_score_relative_strength_vs_spy():
    conn, path = _conn()
    try:
        _seed_bars(conn, "SPY", closes=[100.0 + i * 0.05 for i in range(21)])
        _seed_bars(conn, "AAPL", closes=[100.0 + i * 0.5 for i in range(21)])
        conn.commit()
        rs = score_relative_strength(conn, "AAPL")
        assert rs is not None
        assert rs > 50
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_score_volume_spike_scores_high():
    conn, path = _conn()
    try:
        vols = [1_000_000] * 20 + [2_500_000]
        _seed_bars(conn, "AAPL", closes=[100.0] * 21, volumes=vols)
        conn.commit()
        vol = score_volume(conn, "AAPL")
        assert vol is not None
        assert vol > 70
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_score_dollar_history_strong_history():
    score = score_dollar_history(
        dollar_hit_rate_pct=70.0,
        avg_net_at_high=145.0,
        net_target=150.0,
        days_screened=8,
    )
    assert score >= 65


def test_compute_opportunity_score_returns_factor_breakdown():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-14T12:00:00+00:00",
                "spy_change_pct": 0.3,
                "dia_change_pct": 0.2,
                "qqq_change_pct": 0.4,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "OK",
            },
        )
        _seed_bars(conn, "SPY", closes=[100 + i * 0.1 for i in range(22)])
        _seed_bars(conn, "AAPL", closes=[100 + i * 0.4 for i in range(22)])
        conn.commit()
        result = compute_opportunity_score(
            conn,
            ticker="AAPL",
            live_pass=True,
            near_swing=True,
            meets_liquidity=True,
            adv_dollar=25_000_000,
            avg_range_pct=3.0,
            days_screened=10,
            dollar_hit_rate_pct=65.0,
            avg_net_at_high=140.0,
            net_target=150.0,
        )
        assert 0 <= result["opportunity_score"] <= 100
        assert "market_regime" in result["factor_scores"]
        assert "momentum" in result["factor_scores"]
        assert result["opportunity_floor"] == OPPORTUNITY_FLOOR
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_ranked_candidates_sorted_by_opportunity_score():
    conn, path = _conn()
    try:
        load_preset_into_watchlist(conn, "starter10")
        now = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA", "SPY", "DIA", "QQQ"], end=now)
        insert_regime_snapshot(
            conn,
            {
                "captured_at": now.replace(microsecond=0).isoformat(),
                "spy_change_pct": 0.5,
                "dia_change_pct": 0.3,
                "qqq_change_pct": 0.4,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "OK",
            },
        )
        for ticker in ("AAPL", "MSFT", "NVDA"):
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now.replace(microsecond=0).isoformat(),
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
        result = build_ranked_candidates(
            conn,
            period_days=14,
            require_dollar_rank_gate=False,
            require_opportunity_floor=False,
        )
        ranked = result["ranked"]
        assert ranked
        assert "opportunity_score" in ranked[0]
        assert "factor_scores" in ranked[0]
        scores = [r["opportunity_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)
        assert result["opportunity_floor"] == OPPORTUNITY_FLOOR
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_require_opportunity_floor_excludes_low_scores():
    conn, path = _conn()
    try:
        load_preset_into_watchlist(conn, "starter10")
        now = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "SPY", "DIA", "QQQ"], end=now)
        insert_regime_snapshot(
            conn,
            {
                "captured_at": now.replace(microsecond=0).isoformat(),
                "spy_change_pct": -1.0,
                "dia_change_pct": -0.8,
                "qqq_change_pct": -0.6,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "Blocked",
            },
        )
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
                "computed_at": now.replace(microsecond=0).isoformat(),
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
        result = build_ranked_candidates(
            conn,
            period_days=14,
            require_dollar_rank_gate=False,
            require_opportunity_floor=True,
        )
        assert result["ranked"] == [] or all(
            r["opportunity_score"] >= OPPORTUNITY_FLOOR for r in result["ranked"]
        )
        floor_excluded = [
            e for e in result["excluded"] if e.get("excluded_reason") == "opportunity_floor"
        ]
        assert floor_excluded or not result["ranked"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_news_significance_factor_included():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-14T12:00:00+00:00",
                "spy_change_pct": 0.2,
                "dia_change_pct": 0.1,
                "qqq_change_pct": 0.3,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "OK",
            },
        )
        _seed_bars(conn, "SPY", closes=[100.0] * 21)
        _seed_bars(conn, "AAPL", closes=[100.0] * 21)
        published = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        insert_news_headline(
            conn,
            {
                "ticker": "AAPL",
                "headline_hash": headline_hash("Apple beats Q2 earnings estimates"),
                "published_at": published,
                "headline": "Apple beats Q2 earnings estimates",
                "summary": "EPS beat",
                "source": "Reuters",
                "url": "https://example.com",
                "ingested_at": published,
            },
        )
        conn.commit()
        result = compute_opportunity_score(
            conn,
            ticker="AAPL",
            live_pass=True,
            near_swing=True,
            meets_liquidity=True,
            adv_dollar=20_000_000,
            avg_range_pct=3.0,
            days_screened=5,
            dollar_hit_rate_pct=50.0,
            avg_net_at_high=130.0,
            net_target=150.0,
        )
        assert result["factor_scores"]["news_significance"] is not None
        assert result["factor_scores"]["earnings_events"] == 100.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_high_quality_candidate_passes_floor():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-14T12:00:00+00:00",
                "spy_change_pct": 0.5,
                "dia_change_pct": 0.4,
                "qqq_change_pct": 0.6,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "OK",
            },
        )
        _seed_bars(conn, "SPY", closes=[100 + i * 0.15 for i in range(22)])
        _seed_bars(conn, "NVDA", closes=[100 + i * 0.9 for i in range(22)])
        conn.commit()
        result = compute_opportunity_score(
            conn,
            ticker="NVDA",
            live_pass=True,
            near_swing=True,
            meets_liquidity=True,
            adv_dollar=40_000_000,
            avg_range_pct=3.0,
            days_screened=12,
            dollar_hit_rate_pct=75.0,
            avg_net_at_high=160.0,
            net_target=150.0,
        )
        assert result["opportunity_score"] >= OPPORTUNITY_FLOOR
        assert result["passes_opportunity_floor"] is True
    finally:
        conn.close()
        path.unlink(missing_ok=True)
