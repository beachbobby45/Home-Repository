"""Company news ingest and deterministic significance scoring (Phase 1 Increment 2)."""

from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from investment_agent.config import Settings
from investment_agent.db import (
    insert_news_headline,
    list_news_headlines,
    log_ingest,
    purge_news_older_than,
)
from investment_agent.journal import get_open_positions
from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now

NEWS_RETENTION_DAYS = 30
NEWS_LOOKBACK_DAYS = 7
RANKED_NEWS_LIMIT = 50

EARNINGS_PATTERN = re.compile(
    r"\b(earnings|eps|guidance|conference call|results|beat estimates|miss estimates)\b",
    re.IGNORECASE,
)
MAJOR_KEYWORD_PATTERN = re.compile(
    r"\b("
    r"merger|acquisition|fda|lawsuit|bankruptcy|investigation|sec|downgrade|upgrade|"
    r"recall|halt|delist|bankrupt|subpoena|ceo|layoff|layoffs|guidance cut|guidance raise"
    r")\b",
    re.IGNORECASE,
)


def normalize_headline(headline: str) -> str:
    return " ".join(headline.lower().split())


def headline_hash(headline: str) -> str:
    normalized = normalize_headline(headline)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _published_iso_from_finnhub(item: dict) -> str:
    ts = item.get("datetime")
    if ts is None:
        return fh_now()
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.replace(microsecond=0).isoformat()
    except (TypeError, ValueError, OSError):
        return fh_now()


def finnhub_item_to_row(ticker: str, item: dict, *, ingested_at: str | None = None) -> dict:
    headline = (item.get("headline") or "").strip()
    if not headline:
        raise ValueError("Missing headline")
    return {
        "ticker": ticker.upper(),
        "headline_hash": headline_hash(headline),
        "published_at": _published_iso_from_finnhub(item),
        "headline": headline,
        "summary": (item.get("summary") or "").strip() or None,
        "source": (item.get("source") or "").strip() or None,
        "url": (item.get("url") or "").strip() or None,
        "ingested_at": ingested_at or fh_now(),
    }


def resolve_news_tickers(conn: sqlite3.Connection, *, limit: int = RANKED_NEWS_LIMIT) -> list[str]:
    """Top ranked candidates plus any open positions."""
    from investment_agent.period_screener import build_ranked_candidates

    tickers: set[str] = set()
    ranked = build_ranked_candidates(conn, period_days=14).get("ranked") or []
    for row in ranked[:limit]:
        sym = (row.get("ticker") or "").upper().strip()
        if sym:
            tickers.add(sym)
    for pos in get_open_positions(conn):
        sym = (pos.get("ticker") or "").upper().strip()
        if sym:
            tickers.add(sym)
    return sorted(tickers)


def purge_stale_news(conn: sqlite3.Connection, *, retention_days: int = NEWS_RETENTION_DAYS) -> int:
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=retention_days)
    ).replace(microsecond=0).isoformat()
    return purge_news_older_than(conn, cutoff)


def fetch_and_store_ticker_news(
    conn: sqlite3.Connection,
    client: FinnhubClient,
    ticker: str,
    *,
    lookback_days: int = NEWS_LOOKBACK_DAYS,
) -> dict:
    """Fetch Finnhub company news for one ticker and dedupe into DB."""
    sym = ticker.upper()
    now = datetime.now(timezone.utc)
    to_date = now.strftime("%Y-%m-%d")
    from_date = (now - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    ingested_at = fh_now()

    try:
        items = client.get_company_news(sym, from_date=from_date, to_date=to_date)
    except Exception as exc:
        log_ingest(conn, "finnhub_news", "error", f"{sym}: {exc}")
        return {"ticker": sym, "fetched": 0, "inserted": 0, "error": str(exc)}

    inserted = 0
    for item in items:
        try:
            row = finnhub_item_to_row(sym, item, ingested_at=ingested_at)
        except ValueError:
            continue
        if insert_news_headline(conn, row):
            inserted += 1

    log_ingest(
        conn,
        "finnhub_news",
        "ok",
        f"{sym}: fetched {len(items)}, inserted {inserted}",
    )
    return {"ticker": sym, "fetched": len(items), "inserted": inserted, "error": None}


def ingest_news_for_targets(
    conn: sqlite3.Connection,
    settings: Settings,
    *,
    tickers: list[str] | None = None,
    ranked_limit: int = RANKED_NEWS_LIMIT,
) -> dict:
    """Ingest company news for ranked targets + open positions."""
    if not settings.finnhub_api_key:
        return {
            "ok": False,
            "error": "FINNHUB_API_KEY not set",
            "tickers": [],
            "inserted": 0,
        }

    targets = tickers or resolve_news_tickers(conn, limit=ranked_limit)
    summary: dict = {
        "ok": True,
        "tickers": targets,
        "fetched": 0,
        "inserted": 0,
        "purged": 0,
        "errors": [],
        "by_ticker": [],
    }

    if not targets:
        summary["ok"] = True
        summary["purged"] = purge_stale_news(conn)
        return summary

    client = FinnhubClient(settings.finnhub_api_key)
    try:
        for sym in targets:
            result = fetch_and_store_ticker_news(conn, client, sym)
            summary["by_ticker"].append(result)
            summary["fetched"] += int(result.get("fetched") or 0)
            summary["inserted"] += int(result.get("inserted") or 0)
            if result.get("error"):
                summary["errors"].append(f"{sym}: {result['error']}")
    finally:
        client.close()

    summary["purged"] = purge_stale_news(conn)
    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    summary["partial"] = (
        not summary["ok"] and (summary["inserted"] > 0 or summary["fetched"] > 0)
    )
    return summary


def headlines_in_last_hours(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    hours: float = 24.0,
) -> list[dict]:
    since = (
        datetime.now(timezone.utc) - timedelta(hours=hours)
    ).replace(microsecond=0).isoformat()
    return list_news_headlines(conn, ticker, since_iso=since)


def matches_earnings_event(headline: str, summary: str | None = None) -> bool:
    text = f"{headline} {summary or ''}"
    return bool(EARNINGS_PATTERN.search(text))


def has_major_keyword(headline: str, summary: str | None = None) -> bool:
    text = f"{headline} {summary or ''}"
    return bool(MAJOR_KEYWORD_PATTERN.search(text))


def compute_news_significance(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    hours: float = 24.0,
) -> dict:
    """Deterministic v1 news significance score for Opportunity Score (Inc 3)."""
    recent = headlines_in_last_hours(conn, ticker, hours=hours)
    count = len(recent)
    major_hits = sum(
        1 for row in recent if has_major_keyword(row["headline"], row.get("summary"))
    )
    earnings_flag = any(
        matches_earnings_event(row["headline"], row.get("summary")) for row in recent
    )

    if count == 0:
        score = 20
        detail = "No headlines in last 24h"
    elif count == 1:
        score = 60
        detail = "1 headline in last 24h"
    else:
        score = 80
        detail = f"{count} headlines in last 24h"

    if major_hits:
        score = min(100, score + 10 * major_hits)
        detail += f" · {major_hits} major keyword hit(s)"

    if earnings_flag:
        detail += " · earnings/event flagged"

    return {
        "ticker": ticker.upper(),
        "news_significance": score,
        "headline_count_24h": count,
        "major_keyword_hits": major_hits,
        "earnings_events": earnings_flag,
        "detail": detail,
        "recent_headlines": [
            {
                "headline": row["headline"],
                "published_at": row["published_at"],
                "source": row.get("source"),
            }
            for row in recent[:5]
        ],
    }
