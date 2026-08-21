"""AI / Sentiment Service — rule-based default with gated Claude (Phase 1 Inc 6).

No-Claude-first: when ``ANTHROPIC_API_KEY`` is empty, proposals use deterministic
news sentiment and rule-based explanations. Claude is optional (≤10 proposals/day).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from investment_agent.config import Settings
from investment_agent.news_service import (
    has_major_keyword,
    headline_hash,
    headlines_in_last_hours,
    matches_earnings_event,
)

OPPORTUNITY_SCORE_FLOOR = 65

MODEL_RULE_BASED = "rule-based-v1"
MODEL_CLAUDE_HAIKU = "claude-haiku-v1"
MODEL_CLAUDE_SONNET = "claude-sonnet-v1"

MAX_CLAUDE_PROPOSALS_PER_DAY = 10
CLAUDE_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
CACHE_TTL_HOURS = 24

POSITIVE_SENTIMENT_PATTERN = re.compile(
    r"\b(beat|surge|upgrade|raise|growth|record|strong|bullish|outperform|buy rating)\b",
    re.IGNORECASE,
)
NEGATIVE_SENTIMENT_PATTERN = re.compile(
    r"\b(miss|downgrade|cut|lawsuit|recall|layoff|weak|bearish|investigation|subpoena|halt)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProposalEnrichment:
    explanation: str
    explanation_short: str
    model_version: str
    ai_confidence: float
    news_sentiment: float
    news_sentiment_detail: str
    from_cache: bool = False
    claude_used: bool = False


def claude_configured(settings: Settings | None = None) -> bool:
    s = settings or Settings.from_env()
    return bool(s.anthropic_api_key.strip())


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def compute_rule_based_news_sentiment(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    hours: float = 24.0,
) -> tuple[float, str]:
    """Deterministic headline sentiment (0–100) without Claude."""
    recent = headlines_in_last_hours(conn, ticker, hours=hours)
    if not recent:
        return 50.0, "No headlines in last 24h — neutral sentiment"

    pos_hits = 0
    neg_hits = 0
    for row in recent:
        text = f"{row['headline']} {row.get('summary') or ''}"
        if POSITIVE_SENTIMENT_PATTERN.search(text):
            pos_hits += 1
        if NEGATIVE_SENTIMENT_PATTERN.search(text):
            neg_hits += 1
        if has_major_keyword(row["headline"], row.get("summary")):
            neg_hits += 1
        if matches_earnings_event(row["headline"], row.get("summary")):
            if POSITIVE_SENTIMENT_PATTERN.search(text):
                pos_hits += 1
            elif NEGATIVE_SENTIMENT_PATTERN.search(text):
                neg_hits += 1

    score = 50.0 + (pos_hits * 12.0) - (neg_hits * 15.0)
    if len(recent) >= 3 and neg_hits == 0:
        score += 5.0
    score = _clamp_score(score)
    detail = (
        f"{len(recent)} headline(s) · {pos_hits} positive / {neg_hits} negative signals (24h)"
    )
    return round(score, 1), detail


def _safe_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_rule_based_explanation(
    *,
    ticker: str,
    row: dict,
    plan: dict,
    risk_headline: str,
    news_sentiment: float,
    news_sentiment_detail: str,
) -> tuple[str, str]:
    score = row.get("opportunity_score")
    if score is None:
        score = row.get("score", 0)
    score = _safe_float(score, 0.0)
    hit = _safe_float(row.get("dollar_hit_rate_pct"), 0.0)
    floor = _safe_float(row.get("opportunity_floor"), OPPORTUNITY_SCORE_FLOOR)
    entry = _safe_float(plan.get("limit_buy_price") or plan.get("entry_price"), 0.0)
    target = _safe_float(plan.get("limit_sell_price") or plan.get("target_price"), 0.0)
    net = _safe_float(plan.get("net_at_target"), 0.0)

    short = (
        f"{ticker} — score {score:.0f} · sentiment {news_sentiment:.0f} · "
        f"limit ${entry:.2f}"
    )
    detail = (
        f"Opportunity score {score:.0f}/100 (floor {floor:.0f}). "
        f"${hit:.0f}% historical $ hit rate. "
        f"News sentiment {news_sentiment:.0f}/100 — {news_sentiment_detail}. "
        f"Limit buy ${entry:.2f} → sell ${target:.2f} "
        f"(~${net:.0f} net). "
        f"Risk: {risk_headline}. "
        f"(Rule-based explanation — add ANTHROPIC_API_KEY for Claude narratives.)"
    )
    return detail, short


def _top_headlines(conn: sqlite3.Connection, ticker: str, *, limit: int = 3) -> list[dict]:
    return headlines_in_last_hours(conn, ticker, hours=24.0)[:limit]


def _combined_headline_hash(headlines: list[dict]) -> str:
    parts = sorted(
        row.get("headline_hash") or headline_hash(row.get("headline", ""))
        for row in headlines
    )
    payload = "|".join(parts) if parts else "none"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cache_key(ticker: str, session_date_et: str, headline_bundle_hash: str) -> str:
    return f"{ticker.upper()}:{session_date_et}:{headline_bundle_hash}"


def get_cached_enrichment(conn: sqlite3.Connection, cache_key: str) -> ProposalEnrichment | None:
    row = conn.execute(
        """
        SELECT model_version, explanation, explanation_short, ai_confidence, news_sentiment
        FROM ai_explanation_cache
        WHERE cache_key = ?
          AND datetime(created_at) >= datetime('now', ?)
        """,
        (cache_key, f"-{CACHE_TTL_HOURS} hours"),
    ).fetchone()
    if not row:
        return None
    return ProposalEnrichment(
        explanation=row["explanation"],
        explanation_short=row["explanation_short"],
        model_version=row["model_version"],
        ai_confidence=float(row["ai_confidence"] or 0),
        news_sentiment=float(row["news_sentiment"] or 50),
        news_sentiment_detail="From cache",
        from_cache=True,
        claude_used=str(row["model_version"]).startswith("claude-"),
    )


def store_enrichment_cache(
    conn: sqlite3.Connection,
    *,
    cache_key: str,
    ticker: str,
    session_date_et: str,
    headline_hash_value: str,
    enrichment: ProposalEnrichment,
) -> None:
    conn.execute(
        """
        INSERT INTO ai_explanation_cache (
          cache_key, ticker, session_date_et, headline_hash,
          model_version, explanation, explanation_short,
          ai_confidence, news_sentiment, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cache_key) DO UPDATE SET
          model_version = excluded.model_version,
          explanation = excluded.explanation,
          explanation_short = excluded.explanation_short,
          ai_confidence = excluded.ai_confidence,
          news_sentiment = excluded.news_sentiment,
          created_at = excluded.created_at
        """,
        (
            cache_key,
            ticker.upper(),
            session_date_et,
            headline_hash_value,
            enrichment.model_version,
            enrichment.explanation,
            enrichment.explanation_short,
            enrichment.ai_confidence,
            enrichment.news_sentiment,
            _utc_now(),
        ),
    )


def count_claude_calls_today(conn: sqlite3.Connection, session_date_et: str) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS n FROM ai_explanation_cache
        WHERE session_date_et = ?
          AND model_version LIKE 'claude-%'
        """,
        (session_date_et,),
    ).fetchone()
    return int(row["n"]) if row else 0


def ai_service_status(conn: sqlite3.Connection, session_date_et: str) -> dict:
    settings = Settings.from_env()
    configured = claude_configured(settings)
    used = count_claude_calls_today(conn, session_date_et)
    return {
        "claude_configured": configured,
        "claude_calls_today": used,
        "claude_daily_limit": MAX_CLAUDE_PROPOSALS_PER_DAY,
        "claude_calls_remaining": max(0, MAX_CLAUDE_PROPOSALS_PER_DAY - used),
        "default_model": MODEL_RULE_BASED if not configured else MODEL_CLAUDE_HAIKU,
        "rule_based_fallback": True,
        "note": (
            "Claude explanations disabled — using rule-based text."
            if not configured
            else f"Claude gated to {MAX_CLAUDE_PROPOSALS_PER_DAY} proposals/day."
        ),
    }


def _build_claude_prompt(
    *,
    ticker: str,
    headlines: list[dict],
    factor_scores: dict,
    plan: dict,
    news_sentiment: float,
) -> str:
    headline_lines = "\n".join(
        f"- {row['headline']}" for row in headlines[:3]
    ) or "- (no recent headlines)"
    return (
        f"You are a trading copilot for a human-approved intraday/swing system. "
        f"Analyze {ticker} and respond with JSON only (no markdown):\n"
        f'{{"explanation_short": "one line", "explanation": "2-4 sentences", '
        f'"ai_confidence": 0-100, "news_sentiment": 0-100}}\n\n'
        f"Headlines (24h):\n{headline_lines}\n\n"
        f"Factor scores: {json.dumps(factor_scores, default=str)}\n"
        f"Rule-based news sentiment: {news_sentiment}\n"
        f"Plan: limit buy {plan.get('limit_buy_price')}, sell {plan.get('limit_sell_price')}, "
        f"stop {plan.get('stop_price')}, shares {plan.get('shares')}\n"
        f"Do not recommend execution; explain setup only."
    )


def _parse_claude_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _call_claude_enrichment(
    *,
    settings: Settings,
    ticker: str,
    headlines: list[dict],
    factor_scores: dict,
    plan: dict,
    news_sentiment: float,
    model: str = CLAUDE_DEFAULT_MODEL,
) -> ProposalEnrichment:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = _build_claude_prompt(
        ticker=ticker,
        headlines=headlines,
        factor_scores=factor_scores,
        plan=plan,
        news_sentiment=news_sentiment,
    )
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    payload = _parse_claude_json("".join(text_blocks))
    model_version = MODEL_CLAUDE_HAIKU if "haiku" in model else MODEL_CLAUDE_SONNET
    ai_conf = _clamp_score(float(payload.get("ai_confidence", 0)))
    sent = _clamp_score(float(payload.get("news_sentiment", news_sentiment)))
    return ProposalEnrichment(
        explanation=str(payload.get("explanation") or "").strip(),
        explanation_short=str(payload.get("explanation_short") or "").strip(),
        model_version=model_version,
        ai_confidence=round(ai_conf, 1),
        news_sentiment=round(sent, 1),
        news_sentiment_detail="Claude-assessed sentiment",
        claude_used=True,
    )


def enrich_proposal(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    session_date_et: str,
    row: dict,
    plan: dict,
    risk_headline: str,
    settings: Settings | None = None,
    allow_claude: bool = True,
) -> ProposalEnrichment:
    """Build explanation + sentiment for a trade proposal (rule-based or Claude)."""
    settings = settings or Settings.from_env()
    sym = ticker.upper()

    news_sentiment, sentiment_detail = compute_rule_based_news_sentiment(conn, sym)
    headlines = _top_headlines(conn, sym)
    bundle_hash = _combined_headline_hash(headlines)
    cache_key = _cache_key(sym, session_date_et, bundle_hash)

    cached = get_cached_enrichment(conn, cache_key)
    if cached:
        return cached

    rule_detail, rule_short = build_rule_based_explanation(
        ticker=sym,
        row=row,
        plan=plan,
        risk_headline=risk_headline,
        news_sentiment=news_sentiment,
        news_sentiment_detail=sentiment_detail,
    )
    rule_result = ProposalEnrichment(
        explanation=rule_detail,
        explanation_short=rule_short,
        model_version=MODEL_RULE_BASED,
        ai_confidence=0.0,
        news_sentiment=news_sentiment,
        news_sentiment_detail=sentiment_detail,
    )

    use_claude = (
        allow_claude
        and claude_configured(settings)
        and count_claude_calls_today(conn, session_date_et) < MAX_CLAUDE_PROPOSALS_PER_DAY
    )
    if not use_claude:
        store_enrichment_cache(
            conn,
            cache_key=cache_key,
            ticker=sym,
            session_date_et=session_date_et,
            headline_hash_value=bundle_hash,
            enrichment=rule_result,
        )
        return rule_result

    try:
        claude_result = _call_claude_enrichment(
            settings=settings,
            ticker=sym,
            headlines=headlines,
            factor_scores=row.get("factor_scores") or {},
            plan=plan,
            news_sentiment=news_sentiment,
        )
        if not claude_result.explanation or not claude_result.explanation_short:
            raise ValueError("Claude returned empty explanation")
        store_enrichment_cache(
            conn,
            cache_key=cache_key,
            ticker=sym,
            session_date_et=session_date_et,
            headline_hash_value=bundle_hash,
            enrichment=claude_result,
        )
        return claude_result
    except Exception:
        store_enrichment_cache(
            conn,
            cache_key=cache_key,
            ticker=sym,
            session_date_et=session_date_et,
            headline_hash_value=bundle_hash,
            enrichment=rule_result,
        )
        return rule_result
