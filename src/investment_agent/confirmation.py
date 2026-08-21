"""Candidate Confirmation Engine — per-stock AM confirmation (Phase 1B Inc 13).

Scores ranked #1–#3 against intraday proxies. Confirmation never overrides a
NO TRADE day from Market Activity. Pass threshold: ≥75 on strong days (MA ≥70),
≥70 on average days (MA 60–69).

See docs/PHASE1B_MARKET_ACTIVITY.md §3.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from statistics import mean
from zoneinfo import ZoneInfo

from investment_agent.market_activity import (
    GO_SESSION_MIN,
    SPY_BENCHMARK,
    _score_from_relative,
    today_et_str,
)
from investment_agent.opportunity_score import (
    composite_opportunity_score,
    score_momentum,
    score_news_significance,
    score_relative_strength,
    score_volume,
)
from investment_agent.quote_snapshots import get_snapshots_for_tickers
from investment_agent.regime import intraday_change_pct

ET = ZoneInfo("America/New_York")

CONFIRMATION_PASS_MIN = 75
CONFIRMATION_PASS_CAUTION_MIN = 70
RANKED_CONFIRMATION_LIMIT = 3


def confirmation_pass_threshold(market_activity: dict) -> int:
    """Minimum confirmation score to PASS — lower bar on average market days."""
    score = market_activity.get("score")
    if market_activity.get("band") == "average":
        return CONFIRMATION_PASS_CAUTION_MIN
    if score is not None and int(score) < GO_SESSION_MIN:
        return CONFIRMATION_PASS_CAUTION_MIN
    return CONFIRMATION_PASS_MIN

CONFIRMATION_WEIGHTS: dict[str, float] = {
    "relative_volume": 20.0,
    "volume_acceleration": 15.0,
    "price_momentum": 15.0,
    "relative_strength": 15.0,
    "vwap": 10.0,  # n/a v0
    "breakout_technical": 10.0,
    "sector_confirmation": 5.0,
    "news_catalyst": 10.0,
}

V0_ACTIVE_WEIGHTS = {k: v for k, v in CONFIRMATION_WEIGHTS.items() if k != "vwap"}

SECTOR_TO_ETF = {
    "technology": "XLK",
    "information technology": "XLK",
    "financial": "XLF",
    "financials": "XLF",
    "energy": "XLE",
    "health care": "XLV",
    "healthcare": "XLV",
    "industrials": "XLI",
    "industrial": "XLI",
    "consumer discretionary": "XLY",
    "consumer staples": "XLP",
    "utilities": "XLU",
    "materials": "XLB",
    "real estate": "XLRE",
    "communication": "XLC",
    "communications": "XLC",
}


def now_et() -> datetime:
    return datetime.now(ET)


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _resolve_ticker_quote(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    session_date_et: str,
    live_quotes: dict[str, dict] | None = None,
) -> dict | None:
    sym = ticker.upper()
    snaps = get_snapshots_for_tickers(conn, [sym], session_date_et=session_date_et)
    slot_order = ("plus_15m", "at_open", "pre_market")
    for slot in slot_order:
        row = (snaps.get(sym) or {}).get(slot)
        if row and row.get("price"):
            return row
    if live_quotes and sym in live_quotes and live_quotes[sym].get("price"):
        return live_quotes[sym]
    row = conn.execute(
        """
        SELECT price, open, high, low, prev_close, captured_at
        FROM quotes
        WHERE ticker = ?
        ORDER BY captured_at DESC
        LIMIT 1
        """,
        (sym,),
    ).fetchone()
    if not row:
        return None
    return {
        "price": float(row["price"]),
        "open": float(row["open"]) if row["open"] is not None else None,
        "high": float(row["high"]) if row["high"] is not None else None,
        "low": float(row["low"]) if row["low"] is not None else None,
        "prev_close": float(row["prev_close"]) if row["prev_close"] is not None else None,
        "captured_at": row["captured_at"],
    }


def _spy_intraday_change(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    live_quotes: dict[str, dict] | None = None,
) -> float | None:
    quote = _resolve_ticker_quote(
        conn, SPY_BENCHMARK, session_date_et=session_date_et, live_quotes=live_quotes
    )
    if not quote or quote.get("price") is None:
        return None
    return intraday_change_pct(float(quote["price"]), quote.get("open"), quote.get("prev_close"))


def score_price_momentum(quote: dict | None) -> float | None:
    if not quote or quote.get("price") is None:
        return None
    change = intraday_change_pct(
        float(quote["price"]),
        quote.get("open"),
        quote.get("prev_close"),
    )
    return _score_from_relative(change, scale=2.5)


def score_intraday_relative_strength(
    quote: dict | None,
    spy_change_pct: float | None,
) -> float | None:
    if not quote or quote.get("price") is None or spy_change_pct is None:
        return None
    change = intraday_change_pct(
        float(quote["price"]),
        quote.get("open"),
        quote.get("prev_close"),
    )
    return _score_from_relative(change - spy_change_pct, scale=2.0)


def score_volume_acceleration(
    quote: dict | None,
    *,
    avg_range_pct: float | None = None,
) -> float | None:
    if not quote:
        return None
    open_px = quote.get("open")
    high = quote.get("high")
    low = quote.get("low")
    if not open_px or open_px <= 0 or high is None or low is None:
        return None
    session_range_pct = ((float(high) - float(low)) / float(open_px)) * 100.0
    baseline = avg_range_pct if avg_range_pct and avg_range_pct > 0 else 1.5
    ratio = session_range_pct / baseline
    return _clamp(50.0 + (ratio - 1.0) * 30.0)


def score_breakout_technical(
    quote: dict | None,
    *,
    live_pass: bool = False,
    near_swing: bool = False,
) -> float | None:
    if not quote or quote.get("price") is None:
        return None
    price = float(quote["price"])
    high = quote.get("high")
    open_px = quote.get("open")
    parts: list[float] = []
    if live_pass:
        parts.append(35.0)
    if near_swing:
        parts.append(25.0)
    if high and high > 0:
        proximity = price / float(high)
        parts.append(_clamp(proximity * 40.0))
    elif open_px and open_px > 0:
        parts.append(_clamp(50.0 + ((price - float(open_px)) / float(open_px)) * 500.0))
    if not parts:
        return None
    return _clamp(mean(parts))


def _sector_etf_for_ticker(conn: sqlite3.Connection, ticker: str) -> str | None:
    row = conn.execute(
        "SELECT sector FROM watchlist WHERE ticker = ? AND active = 1",
        (ticker.upper(),),
    ).fetchone()
    if not row or not row["sector"]:
        return None
    return SECTOR_TO_ETF.get(str(row["sector"]).strip().lower())


def score_sector_confirmation(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    session_date_et: str,
    live_quotes: dict[str, dict] | None = None,
) -> float | None:
    etf = _sector_etf_for_ticker(conn, ticker)
    if not etf:
        return None
    sector_quote = _resolve_ticker_quote(
        conn, etf, session_date_et=session_date_et, live_quotes=live_quotes
    )
    spy_change = _spy_intraday_change(conn, session_date_et=session_date_et, live_quotes=live_quotes)
    if not sector_quote or spy_change is None:
        return None
    sector_change = intraday_change_pct(
        float(sector_quote["price"]),
        sector_quote.get("open"),
        sector_quote.get("prev_close"),
    )
    return _score_from_relative(sector_change - spy_change, scale=2.0)


def evaluate_ticker_confirmation(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    market_activity: dict,
    candidate_row: dict | None = None,
    live_quotes: dict[str, dict] | None = None,
    when: datetime | None = None,
) -> dict:
    """Score one ticker and determine PASS / FAIL vs day authorization."""
    dt = when or now_et()
    session_date = today_et_str(dt)
    sym = ticker.upper()
    quote = _resolve_ticker_quote(conn, sym, session_date_et=session_date, live_quotes=live_quotes)
    row = candidate_row or {}
    spy_change = _spy_intraday_change(conn, session_date_et=session_date, live_quotes=live_quotes)
    avg_range = float(row.get("avg_range_pct") or 0) or None

    factor_scores: dict[str, float | None] = {
        "relative_volume": score_volume(conn, sym),
        "volume_acceleration": score_volume_acceleration(quote, avg_range_pct=avg_range),
        "price_momentum": score_price_momentum(quote),
        "relative_strength": score_intraday_relative_strength(quote, spy_change)
        or score_relative_strength(conn, sym),
        "breakout_technical": score_breakout_technical(
            quote,
            live_pass=bool(row.get("live_pass_today")),
            near_swing=bool(row.get("near_swing_target") or row.get("near_swing")),
        ),
        "sector_confirmation": score_sector_confirmation(
            conn, sym, session_date_et=session_date, live_quotes=live_quotes
        ),
        "news_catalyst": score_news_significance(conn, sym),
    }
    score, used_weights = composite_opportunity_score(factor_scores, weights=V0_ACTIVE_WEIGHTS)
    day_allows = bool(market_activity.get("allow_trade"))
    pass_min = confirmation_pass_threshold(market_activity)
    passes = day_allows and score >= pass_min

    return {
        "ticker": sym,
        "score": score,
        "passes": passes,
        "pass_threshold": pass_min,
        "blocked_by_day": not day_allows,
        "opportunity_score": row.get("score") or row.get("rank_score"),
        "components": {
            name: round(val, 1) if val is not None else None for name, val in factor_scores.items()
        },
        "weights_used": used_weights,
        "summary": _build_summary(sym, score, passes, day_allows, market_activity, pass_min),
    }


def _build_summary(
    ticker: str,
    score: int,
    passes: bool,
    day_allows: bool,
    market_activity: dict,
    pass_min: int,
) -> str:
    if not day_allows:
        return f"{ticker} {score}/100 — day NO TRADE (confirmation pending)"
    if passes:
        return f"{ticker} {score}/100 — PASS (confirms today)"
    return f"{ticker} {score}/100 — FAIL (below {pass_min} threshold)"


def get_ranked_confirmation_targets(
    conn: sqlite3.Connection,
    *,
    limit: int = RANKED_CONFIRMATION_LIMIT,
) -> list[dict]:
    from investment_agent.trading_day import _live_ranked_candidates

    return _live_ranked_candidates(conn, limit=limit)


def evaluate_session_confirmations(
    conn: sqlite3.Connection,
    *,
    market_activity: dict,
    live_quotes: dict[str, dict] | None = None,
    when: datetime | None = None,
    limit: int = RANKED_CONFIRMATION_LIMIT,
    persist: bool = False,
) -> list[dict]:
    """Evaluate confirmation for ranked #1–#3 live candidates."""
    dt = when or now_et()
    session_date = today_et_str(dt)
    targets = get_ranked_confirmation_targets(conn, limit=limit)
    results: list[dict] = []
    for idx, row in enumerate(targets):
        result = evaluate_ticker_confirmation(
            conn,
            row["ticker"],
            market_activity=market_activity,
            candidate_row=row,
            live_quotes=live_quotes,
            when=dt,
        )
        result["rank"] = idx + 1
        result["eligible"] = rank_eligible(idx, market_activity.get("band"))
        results.append(result)
        if persist:
            save_confirmation_evaluation(
                conn,
                session_date_et=session_date,
                captured_at=dt.replace(microsecond=0).isoformat(),
                ticker=result["ticker"],
                rank=idx + 1,
                score=result["score"],
                passes=result["passes"],
                blocked_by_day=result["blocked_by_day"],
                components=result.get("components") or {},
                summary=result.get("summary") or "",
            )
    return results


def rank_eligible(rank_index: int, market_band: str | None) -> bool:
    """Exceptional day: #1–#3; Above average: #1 only."""
    if market_band == "exceptional":
        return rank_index < RANKED_CONFIRMATION_LIMIT
    return rank_index == 0


def _rank_eligible(rank_index: int, market_band: str | None) -> bool:
    return rank_eligible(rank_index, market_band)


def confirmation_allows_ticker(
    confirmations: list[dict],
    ticker: str,
    *,
    market_band: str | None,
) -> bool:
    for item in confirmations:
        if item.get("ticker") != ticker.upper():
            continue
        rank_index = int(item.get("rank", 1)) - 1
        if not rank_eligible(rank_index, market_band):
            return False
        return bool(item.get("passes"))
    return False


def save_confirmation_evaluation(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    captured_at: str,
    ticker: str,
    rank: int,
    score: int,
    passes: bool,
    blocked_by_day: bool,
    components: dict,
    summary: str,
) -> None:
    conn.execute(
        """
        INSERT INTO confirmation_evaluations
          (session_date_et, captured_at, ticker, rank, score, passes,
           blocked_by_day, components_json, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_date_et,
            captured_at,
            ticker.upper(),
            rank,
            score,
            1 if passes else 0,
            1 if blocked_by_day else 0,
            json.dumps(components),
            summary,
        ),
    )


def list_recent_confirmations(
    conn: sqlite3.Connection,
    session_date_et: str,
    *,
    limit: int = 10,
) -> list[dict]:
    rows = conn.execute(
        """
        SELECT captured_at, ticker, rank, score, passes, blocked_by_day, summary
        FROM confirmation_evaluations
        WHERE session_date_et = ?
        ORDER BY captured_at DESC, rank ASC
        LIMIT ?
        """,
        (session_date_et, limit),
    ).fetchall()
    return [
        {
            "captured_at": row["captured_at"],
            "ticker": row["ticker"],
            "rank": int(row["rank"]),
            "score": int(row["score"]),
            "passes": bool(row["passes"]),
            "blocked_by_day": bool(row["blocked_by_day"]),
            "summary": row["summary"],
        }
        for row in rows
    ]


def confirmations_to_dict(results: list[dict]) -> list[dict]:
    return [
        {
            "rank": item.get("rank"),
            "ticker": item.get("ticker"),
            "score": item.get("score"),
            "passes": item.get("passes"),
            "pass_threshold": item.get("pass_threshold"),
            "eligible": item.get("eligible"),
            "blocked_by_day": item.get("blocked_by_day"),
            "opportunity_score": item.get("opportunity_score"),
            "summary": item.get("summary"),
            "components": item.get("components") or {},
        }
        for item in results
    ]
