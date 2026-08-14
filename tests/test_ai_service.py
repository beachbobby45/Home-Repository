"""Tests for Phase 1 AI Sentiment Service (Increment 6, no-Claude-first)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.ai_service import (
    MODEL_CLAUDE_HAIKU,
    MODEL_RULE_BASED,
    MAX_CLAUDE_PROPOSALS_PER_DAY,
    ProposalEnrichment,
    ai_service_status,
    build_rule_based_explanation,
    claude_configured,
    compute_rule_based_news_sentiment,
    enrich_proposal,
    get_cached_enrichment,
    store_enrichment_cache,
)
from investment_agent.config import Settings
from investment_agent.dashboard.app import app
from investment_agent.db import init_db, insert_news_headline
from investment_agent.news_service import headline_hash
from investment_agent.opportunity_score import (
    composite_opportunity_score,
    finalize_proposal_factor_scores,
)

NOW = datetime.now(timezone.utc).replace(microsecond=0)


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _insert_headline(conn, ticker: str, headline: str, *, hours_ago: float = 1.0):
    published = (NOW - timedelta(hours=hours_ago)).isoformat()
    insert_news_headline(
        conn,
        {
            "ticker": ticker,
            "headline_hash": headline_hash(headline),
            "published_at": published,
            "headline": headline,
            "summary": None,
            "source": "test",
            "url": None,
            "ingested_at": NOW.isoformat(),
        },
    )


def test_claude_not_configured_by_default():
    settings = Settings(
        anthropic_api_key="",
        fred_api_key="x",
        finnhub_api_key="x",
        massive_api_key=None,
        verify_test_ticker="SPY",
        app_api_key="",
        alpaca_api_key=None,
        alpaca_secret_key=None,
    )
    assert claude_configured(settings) is False


def test_rule_based_sentiment_neutral_without_headlines():
    conn, path = _conn()
    try:
        score, detail = compute_rule_based_news_sentiment(conn, "AAPL")
        assert score == 50.0
        assert "neutral" in detail.lower()
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_rule_based_sentiment_positive_headlines():
    conn, path = _conn()
    try:
        _insert_headline(conn, "AAPL", "Apple beats earnings estimates with record growth")
        conn.commit()
        score, _detail = compute_rule_based_news_sentiment(conn, "AAPL")
        assert score > 50.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_rule_based_sentiment_negative_headlines():
    conn, path = _conn()
    try:
        _insert_headline(conn, "AAPL", "Apple faces lawsuit and downgrade after weak guidance")
        conn.commit()
        score, _detail = compute_rule_based_news_sentiment(conn, "AAPL")
        assert score < 50.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_enrich_proposal_rule_based_without_claude_key():
    conn, path = _conn()
    try:
        row = {"opportunity_score": 72, "dollar_hit_rate_pct": 55, "factor_scores": {}}
        plan = {
            "limit_buy_price": 100.0,
            "limit_sell_price": 102.0,
            "stop_price": 99.25,
            "shares": 100,
            "net_at_target": 150,
        }
        settings = Settings(
            anthropic_api_key="",
            fred_api_key="x",
            finnhub_api_key="x",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        result = enrich_proposal(
            conn,
            ticker="AAPL",
            session_date_et="2026-08-14",
            row=row,
            plan=plan,
            risk_headline="Approved",
            settings=settings,
        )
        assert result.model_version == MODEL_RULE_BASED
        assert result.ai_confidence == 0.0
        assert result.explanation
        assert result.explanation_short
        assert "rule-based" in result.explanation.lower()
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_cache_prevents_duplicate_enrichment():
    conn, path = _conn()
    try:
        cache_key = "AAPL:2026-08-14:abc123"
        cached = ProposalEnrichment(
            explanation="Cached full",
            explanation_short="Cached short",
            model_version=MODEL_RULE_BASED,
            ai_confidence=0.0,
            news_sentiment=55.0,
            news_sentiment_detail="cached",
        )
        store_enrichment_cache(
            conn,
            cache_key=cache_key,
            ticker="AAPL",
            session_date_et="2026-08-14",
            headline_hash_value="abc123",
            enrichment=cached,
        )
        conn.commit()
        hit = get_cached_enrichment(conn, cache_key)
        assert hit is not None
        assert hit.explanation_short == "Cached short"
        assert hit.from_cache is True
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_claude_failure_falls_back_to_rule_based():
    conn, path = _conn()
    try:
        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="x",
            finnhub_api_key="x",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        row = {"opportunity_score": 70, "dollar_hit_rate_pct": 50, "factor_scores": {}}
        plan = {
            "limit_buy_price": 100.0,
            "limit_sell_price": 102.0,
            "stop_price": 99.25,
            "shares": 100,
            "net_at_target": 150,
        }
        with patch("investment_agent.ai_service._call_claude_enrichment", side_effect=RuntimeError("api down")):
            result = enrich_proposal(
                conn,
                ticker="MSFT",
                session_date_et="2026-08-14",
                row=row,
                plan=plan,
                risk_headline="Approved",
                settings=settings,
            )
        assert result.model_version == MODEL_RULE_BASED
        assert result.ai_confidence == 0.0
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_claude_success_when_configured():
    conn, path = _conn()
    try:
        settings = Settings(
            anthropic_api_key="sk-test",
            fred_api_key="x",
            finnhub_api_key="x",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        claude_result = ProposalEnrichment(
            explanation="Claude narrative here.",
            explanation_short="Claude one-liner",
            model_version=MODEL_CLAUDE_HAIKU,
            ai_confidence=82.0,
            news_sentiment=76.0,
            news_sentiment_detail="Claude",
            claude_used=True,
        )
        row = {"opportunity_score": 80, "dollar_hit_rate_pct": 60, "factor_scores": {}}
        plan = {
            "limit_buy_price": 100.0,
            "limit_sell_price": 102.0,
            "stop_price": 99.25,
            "shares": 100,
            "net_at_target": 150,
        }
        with patch("investment_agent.ai_service._call_claude_enrichment", return_value=claude_result):
            result = enrich_proposal(
                conn,
                ticker="NVDA",
                session_date_et="2026-08-14",
                row=row,
                plan=plan,
                risk_headline="Approved",
                settings=settings,
            )
        assert result.model_version == MODEL_CLAUDE_HAIKU
        assert result.ai_confidence == 82.0
        assert result.explanation_short == "Claude one-liner"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_ai_confidence_excluded_from_composite_when_zero():
    scores = {
        "market_regime": 80.0,
        "technical_setup": 70.0,
        "news_sentiment": 60.0,
        "ai_confidence": 0.0,
    }
    composite, used = composite_opportunity_score(scores)
    assert "ai_confidence" not in used
    assert composite > 0


def test_finalize_proposal_factor_scores_includes_sentiment_and_rr():
    conn, path = _conn()
    try:
        scores = finalize_proposal_factor_scores(
            {"market_regime": 80.0},
            conn=conn,
            ticker="AAPL",
            expected_rr=2.0,
            news_sentiment=65.0,
            ai_confidence=None,
        )
        assert scores["news_sentiment"] == 65.0
        assert scores["risk_reward"] is not None
        assert scores["ai_confidence"] is None
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_ai_service_status_no_claude():
    conn, path = _conn()
    try:
        with patch("investment_agent.ai_service.Settings.from_env") as mock_env:
            mock_env.return_value = Settings(
                anthropic_api_key="",
                fred_api_key="x",
                finnhub_api_key="x",
                massive_api_key=None,
                verify_test_ticker="SPY",
                app_api_key="",
                alpaca_api_key=None,
                alpaca_secret_key=None,
            )
            status = ai_service_status(conn, "2026-08-14")
        assert status["claude_configured"] is False
        assert status["claude_calls_today"] == 0
        assert status["claude_daily_limit"] == MAX_CLAUDE_PROPOSALS_PER_DAY
        assert status["rule_based_fallback"] is True
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_api_ai_status():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        init_db(db_path)

        def fake_connect():
            c = sqlite3.connect(db_path)
            c.row_factory = sqlite3.Row
            return c

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                with patch("investment_agent.ai_service.Settings.from_env") as mock_env:
                    mock_env.return_value = Settings(
                        anthropic_api_key="",
                        fred_api_key="x",
                        finnhub_api_key="x",
                        massive_api_key=None,
                        verify_test_ticker="SPY",
                        app_api_key="",
                        alpaca_api_key=None,
                        alpaca_secret_key=None,
                    )
                    client = TestClient(app)
                    resp = client.get("/api/ai/status")
                    assert resp.status_code == 200
                    data = resp.json()
                    assert data["claude_configured"] is False


def test_build_rule_based_explanation_mentions_sentiment():
    detail, short = build_rule_based_explanation(
        ticker="AAPL",
        row={"opportunity_score": 75, "dollar_hit_rate_pct": 60},
        plan={
            "limit_buy_price": 100,
            "limit_sell_price": 102,
            "net_at_target": 150,
        },
        risk_headline="Approved",
        news_sentiment=62.0,
        news_sentiment_detail="2 headlines",
    )
    assert "sentiment 62" in detail
    assert "sentiment 62" in short
