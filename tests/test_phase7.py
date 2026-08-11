"""Tests for Phase 7 watchlist and period screener."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_ohlcv_rows, insert_ticker_metrics
from investment_agent.demo_seed import _seed_ohlcv_history
from investment_agent.period_screener import (
    RANK_WEIGHTS,
    _criteria_likelihood_score,
    build_ranked_candidates,
    date_range_for_period,
    run_period_screener,
    save_screener_run,
)
from investment_agent.watchlist import (
    compute_universe_stats,
    load_preset_into_watchlist,
    load_preset_tickers,
)


def test_load_sp100_preset_has_many_tickers():
    tickers = load_preset_tickers("sp100")
    assert len(tickers) >= 90
    assert "AAPL" in tickers
    assert "SPY" in tickers


def test_load_preset_into_watchlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        result = load_preset_into_watchlist(conn, "starter10")
        conn.commit()
        assert result["tickers_loaded"] == 10
        count = conn.execute("SELECT COUNT(*) AS c FROM watchlist WHERE active = 1").fetchone()["c"]
        assert count == 10
        conn.close()


def test_period_screener_on_seeded_history():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA", "AMD", "META", "SPY", "DIA", "QQQ"], end=now)
        conn.commit()

        start, end = date_range_for_period(14, end_date=(now.replace(day=max(now.day - 1, 1))).strftime("%Y-%m-%d"), conn=conn)
        result = run_period_screener(
            conn,
            start_date=start,
            end_date=end,
            min_days_screened=1,
            requested_trading_days=14,
        )
        assert "candidates" in result
        assert result["days_evaluated"] >= 1

        run_id = save_screener_run(conn, result)
        conn.commit()
        assert run_id >= 1
        conn.close()


def test_criteria_likelihood_score_prefers_live_and_swing():
    high = _criteria_likelihood_score(
        live_pass=True,
        hit_rate_pct=80.0,
        dollar_hit_rate_pct=65.0,
        avg_net_at_high=160.0,
        net_target=150.0,
        days_screened=10,
        avg_range_pct=3.0,
        adv_dollar=10_000_000,
        meets_liquidity=True,
        near_swing=True,
        period_days=14,
    )
    low = _criteria_likelihood_score(
        live_pass=False,
        hit_rate_pct=20.0,
        dollar_hit_rate_pct=10.0,
        avg_net_at_high=50.0,
        net_target=150.0,
        days_screened=2,
        avg_range_pct=1.5,
        adv_dollar=500_000,
        meets_liquidity=False,
        near_swing=False,
        period_days=14,
    )
    assert high["score"] > low["score"]
    assert high["swing_proximity"] == 1.0
    assert low["liquidity_score"] == 0.0


def test_build_ranked_candidates_includes_enriched_fields():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        insert_ticker_metrics(
            conn,
            {
                "ticker": "AAPL",
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
        now_dt = datetime.now(timezone.utc)
        _seed_ohlcv_history(conn, ["AAPL", "MSFT", "NVDA"], end=now_dt)
        conn.commit()

        result = build_ranked_candidates(conn, period_days=14, require_dollar_rank_gate=False)
        assert "ranked" in result
        assert result["rank_weights"] == RANK_WEIGHTS
        assert len(result["ranked"]) >= 1
        top = result["ranked"][0]
        for field in (
            "score",
            "swing_proximity",
            "liquidity_score",
            "consistency_score",
            "adv_dollar_m",
            "meets_liquidity",
            "near_swing_target",
        ):
            assert field in top
        scores = [r["score"] for r in result["ranked"]]
        assert scores == sorted(scores, reverse=True)
        conn.close()


def test_universe_stats_with_metrics():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "p7.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for ticker, swing in [("AAPL", 3.1), ("MSFT", 2.9), ("SPY", 1.2)]:
            insert_ticker_metrics(
                conn,
                {
                    "ticker": ticker,
                    "computed_at": now,
                    "adv_dollar": 50_000_000,
                    "avg_range_pct": swing,
                    "liquidity_cap": 400_000,
                    "last_close": 100,
                    "last_quote": 100,
                    "meets_liquidity_min": True,
                    "near_swing_target": 2.0 <= swing <= 4.0,
                },
            )
        conn.commit()
        stats = compute_universe_stats(conn)
        assert stats["universe_size"] == 10
        assert stats["pass_both_step3"] >= 1
        conn.close()
