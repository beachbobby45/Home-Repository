"""Tests for Phase 1 News Service (Increment 2)."""

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
from investment_agent.db import init_db, insert_news_headline
from investment_agent.ingest import run_ingest
from investment_agent.journal import insert_trade
from investment_agent.news_service import (
    compute_news_significance,
    fetch_and_store_ticker_news,
    finnhub_item_to_row,
    headline_hash,
    ingest_news_for_targets,
    matches_earnings_event,
    normalize_headline,
    purge_stale_news,
    resolve_news_tickers,
)
from investment_agent.providers.finnhub import FinnhubClient
from investment_agent.watchlist import load_preset_into_watchlist


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _recent_iso(hours_ago: float = 1.0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return dt.replace(microsecond=0).isoformat()


def _insert_headline(conn, ticker: str, headline: str, *, hours_ago: float = 1.0) -> bool:
    published = _recent_iso(hours_ago)
    return insert_news_headline(
        conn,
        {
            "ticker": ticker,
            "headline_hash": headline_hash(headline),
            "published_at": published,
            "headline": headline,
            "summary": None,
            "source": "Test",
            "url": "https://example.com",
            "ingested_at": published,
        },
    )


def test_normalize_headline_collapses_whitespace_and_case():
    assert normalize_headline("  Apple  Beats   Earnings  ") == "apple beats earnings"


def test_headline_hash_stable_for_normalized_duplicates():
    h1 = headline_hash("Apple beats earnings")
    h2 = headline_hash("  APPLE   beats   earnings ")
    assert h1 == h2
    assert len(h1) == 64


def test_insert_news_headline_dedupes_by_ticker_and_hash():
    conn, path = _conn()
    try:
        row = finnhub_item_to_row(
            "AAPL",
            {
                "datetime": int(datetime.now(timezone.utc).timestamp()),
                "headline": "Apple launches new product",
                "summary": "Details inside",
                "source": "Reuters",
                "url": "https://example.com/a",
            },
        )
        assert insert_news_headline(conn, row) is True
        assert insert_news_headline(conn, row) is False
        count = conn.execute("SELECT COUNT(*) AS c FROM news_headlines").fetchone()["c"]
        assert count == 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_finnhub_item_to_row_maps_fields():
    ts = int(datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc).timestamp())
    row = finnhub_item_to_row(
        "nvda",
        {
            "datetime": ts,
            "headline": "NVDA guidance raised",
            "summary": "Chip demand strong",
            "source": "Bloomberg",
            "url": "https://example.com/nvda",
        },
        ingested_at="2026-08-14T12:00:00+00:00",
    )
    assert row["ticker"] == "NVDA"
    assert row["headline"] == "NVDA guidance raised"
    assert row["source"] == "Bloomberg"
    assert row["published_at"].startswith("2026-08-14")


def test_compute_news_significance_zero_headlines():
    conn, path = _conn()
    try:
        result = compute_news_significance(conn, "AAPL")
        assert result["news_significance"] == 20
        assert result["headline_count_24h"] == 0
        assert result["earnings_events"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_compute_news_significance_one_headline():
    conn, path = _conn()
    try:
        _insert_headline(conn, "AAPL", "Apple expands services business")
        conn.commit()
        result = compute_news_significance(conn, "AAPL")
        assert result["news_significance"] == 60
        assert result["headline_count_24h"] == 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_compute_news_significance_two_plus_headlines():
    conn, path = _conn()
    try:
        _insert_headline(conn, "AAPL", "Apple supplier update")
        _insert_headline(conn, "AAPL", "Apple store traffic rises")
        conn.commit()
        result = compute_news_significance(conn, "AAPL")
        assert result["news_significance"] >= 80
        assert result["headline_count_24h"] == 2
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_compute_news_significance_major_keyword_boost():
    conn, path = _conn()
    try:
        _insert_headline(conn, "AAPL", "Apple faces SEC investigation")
        _insert_headline(conn, "AAPL", "Analyst downgrade hits shares")
        conn.commit()
        result = compute_news_significance(conn, "AAPL")
        assert result["news_significance"] >= 90
        assert result["major_keyword_hits"] >= 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_matches_earnings_event():
    assert matches_earnings_event("Company reports Q2 earnings beat estimates")
    assert not matches_earnings_event("Company opens new retail location")


def test_compute_news_significance_flags_earnings():
    conn, path = _conn()
    try:
        _insert_headline(conn, "MSFT", "Microsoft Q1 earnings beat estimates")
        conn.commit()
        result = compute_news_significance(conn, "MSFT")
        assert result["earnings_events"] is True
        assert "earnings" in result["detail"].lower()
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_purge_stale_news():
    conn, path = _conn()
    try:
        old = (datetime.now(timezone.utc) - timedelta(days=45)).replace(microsecond=0).isoformat()
        insert_news_headline(
            conn,
            {
                "ticker": "AAPL",
                "headline_hash": headline_hash("Old headline"),
                "published_at": old,
                "headline": "Old headline",
                "summary": None,
                "source": "Test",
                "url": None,
                "ingested_at": old,
            },
        )
        _insert_headline(conn, "AAPL", "Fresh headline")
        conn.commit()
        purged = purge_stale_news(conn, retention_days=30)
        assert purged == 1
        remaining = conn.execute("SELECT COUNT(*) AS c FROM news_headlines").fetchone()["c"]
        assert remaining == 1
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_resolve_news_tickers_includes_ranked_and_open_positions():
    conn, path = _conn()
    try:
        with patch("investment_agent.news_service.build_ranked_candidates") as mock_rank:
            mock_rank.return_value = {
                "ranked": [{"ticker": f"T{i}"} for i in range(55)],
            }
            insert_trade(
                conn,
                ticker="OPEN1",
                side="BUY",
                shares=10,
                price=50,
                executed_at=_recent_iso(2),
            )
            conn.commit()
            tickers = resolve_news_tickers(conn, limit=50)
        assert len(tickers) == 51
        assert "T0" in tickers
        assert "T49" in tickers
        assert "T50" not in tickers
        assert "OPEN1" in tickers
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_fetch_and_store_ticker_news_inserts_new_rows():
    conn, path = _conn()
    try:
        mock_client = MagicMock()
        mock_client.get_company_news.return_value = [
            {
                "datetime": int(datetime.now(timezone.utc).timestamp()),
                "headline": "Fresh headline one",
                "summary": "Summary",
                "source": "Yahoo",
                "url": "https://example.com/1",
            },
            {
                "datetime": int(datetime.now(timezone.utc).timestamp()),
                "headline": "Fresh headline one",
                "summary": "Duplicate",
                "source": "Yahoo",
                "url": "https://example.com/2",
            },
        ]
        result = fetch_and_store_ticker_news(conn, mock_client, "AAPL")
        assert result["fetched"] == 2
        assert result["inserted"] == 1
        assert result["error"] is None
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_ingest_news_for_targets_top_ranked():
    conn, path = _conn()
    try:
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
        with patch("investment_agent.news_service.resolve_news_tickers", return_value=["AAPL", "MSFT"]):
            with patch("investment_agent.news_service.FinnhubClient") as mock_cls:
                mock_client = MagicMock()
                mock_cls.return_value = mock_client
                mock_client.get_company_news.return_value = [
                    {
                        "datetime": int(datetime.now(timezone.utc).timestamp()),
                        "headline": "Ticker news item",
                        "summary": "Body",
                        "source": "Reuters",
                        "url": "https://example.com/x",
                    }
                ]
                summary = ingest_news_for_targets(conn, settings)
        assert summary["ok"] is True
        assert summary["tickers"] == ["AAPL", "MSFT"]
        assert summary["inserted"] == 2
        assert mock_client.close.called
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_ingest_news_for_targets_missing_api_key():
    conn, path = _conn()
    try:
        settings = Settings(
            anthropic_api_key="",
            fred_api_key="",
            finnhub_api_key="",
            massive_api_key=None,
            verify_test_ticker="SPY",
            app_api_key="",
            alpaca_api_key=None,
            alpaca_secret_key=None,
        )
        summary = ingest_news_for_targets(conn, settings)
        assert summary["ok"] is False
        assert "FINNHUB_API_KEY" in summary["error"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_finnhub_client_get_company_news():
    mock_http = MagicMock()
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"headline": "Test", "datetime": 1}]
    mock_resp.raise_for_status = MagicMock()
    mock_http.get.return_value = mock_resp
    client = FinnhubClient("test-key", min_interval_sec=0, client=mock_http)
    rows = client.get_company_news("AAPL", from_date="2026-08-01", to_date="2026-08-14")
    assert len(rows) == 1
    mock_http.get.assert_called_once()
    params = mock_http.get.call_args.kwargs["params"]
    assert params["symbol"] == "AAPL"
    assert params["from"] == "2026-08-01"


def test_run_ingest_calls_news_service():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "news-ingest.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        load_preset_into_watchlist(conn, "starter10")
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
            patch(
                "investment_agent.news_service.ingest_news_for_targets",
                return_value={"ok": True, "tickers": ["AAPL"], "inserted": 3, "errors": []},
            ) as mock_news,
        ):
            summary = run_ingest(settings, db_path=path, incremental=False)

        assert "news" in summary
        assert summary["news"]["inserted"] == 3
        mock_news.assert_called_once()
