"""Deterministic Opportunity Score composite (Phase 1 Increment 3).

Multi-factor 0–100 score replacing period rank as the primary proposal sort key.
Increments 3–4 use deterministic factors only; news_sentiment (12%) is redistributed
to technical_setup and dollar_history until Increment 6. risk_reward (12%) is deferred
to Increment 4 and excluded from nominal weights (renormalized across available factors).
"""

from __future__ import annotations

import sqlite3
from statistics import mean

from investment_agent.account import latest_regime
from investment_agent.liquidity import MIN_ADV_DOLLAR, SWING_TARGET_PCT
from investment_agent.news_service import compute_news_significance

OPPORTUNITY_FLOOR = 65
SPY_BENCHMARK = "SPY"
MOMENTUM_WINDOWS = (5, 10, 20)
RS_WINDOW = 20
VOLUME_WINDOW = 20

# Nominal Phase 1 weights (percent points). Sum = 98; risk_reward (12) deferred to Inc 4.
# news_sentiment (12) redistributed +6 to technical_setup, +6 to dollar_history per spec §5.2.1.
PHASE1_OPPORTUNITY_WEIGHTS: dict[str, float] = {
    "market_regime": 10.0,
    "technical_setup": 21.0,
    "momentum": 10.0,
    "relative_strength": 10.0,
    "volume": 10.0,
    "volatility": 8.0,
    "news_significance": 8.0,
    "earnings_events": 5.0,
    "dollar_history": 16.0,
}


def passes_opportunity_floor(score: float | int | None) -> bool:
    return score is not None and float(score) >= OPPORTUNITY_FLOOR


def composite_opportunity_score(
    factor_scores: dict[str, float | None],
    *,
    weights: dict[str, float] | None = None,
) -> tuple[int, dict[str, float]]:
    """Weighted composite with renormalization when factors are missing."""
    wmap = weights or PHASE1_OPPORTUNITY_WEIGHTS
    available = {
        name: score
        for name, score in factor_scores.items()
        if score is not None and name in wmap
    }
    if not available:
        return 0, {}

    total_weight = sum(wmap[name] for name in available)
    if total_weight <= 0:
        return 0, {}

    weighted_sum = sum(wmap[name] * available[name] for name in available)
    composite = round(weighted_sum / total_weight)
    used_weights = {name: wmap[name] for name in available}
    return int(max(0, min(100, composite))), used_weights


def _fetch_recent_bars(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    limit: int = 21,
) -> list[dict]:
    rows = conn.execute(
        """
        SELECT date, close, volume
        FROM ohlcv_daily
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT ?
        """,
        (ticker.upper(), limit),
    ).fetchall()
    return [
        {"date": row["date"], "close": float(row["close"]), "volume": int(row["volume"])}
        for row in reversed(rows)
    ]


def _return_pct(closes: list[float], days: int) -> float | None:
    if len(closes) < days + 1:
        return None
    start = closes[-(days + 1)]
    end = closes[-1]
    if start <= 0:
        return None
    return ((end - start) / start) * 100.0


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, value))


def _score_from_relative(relative_pct: float, *, scale: float = 3.0) -> float:
    """Map relative % vs benchmark: -scale -> 0, 0 -> 50, +scale -> 100."""
    return _clamp_score(50.0 + (relative_pct / scale) * 50.0)


def score_market_regime(conn: sqlite3.Connection) -> float | None:
    regime = latest_regime(conn)
    if not regime:
        return None
    if regime.get("block_new_longs"):
        return 0.0
    avg_change = mean(
        float(regime.get(key) or 0.0)
        for key in ("spy_change_pct", "dia_change_pct", "qqq_change_pct")
    )
    return _score_from_relative(avg_change, scale=2.0)


def score_technical_setup(
    *,
    live_pass: bool,
    near_swing: bool,
    meets_liquidity: bool,
    adv_dollar: float,
    days_screened: int,
    period_days: int = 14,
) -> float:
    liquidity_ratio = min(1.0, adv_dollar / (MIN_ADV_DOLLAR * 5)) if meets_liquidity and adv_dollar > 0 else 0.0
    consistency = min(days_screened / max(period_days * 0.5, 1), 1.0)
    parts = [
        40.0 if live_pass else 0.0,
        20.0 if near_swing else 0.0,
        20.0 * liquidity_ratio,
        20.0 * consistency,
    ]
    return _clamp_score(sum(parts))


def score_volatility(avg_range_pct: float) -> float:
    if avg_range_pct <= 0:
        return 0.0
    proximity = max(0.0, 1.0 - abs(avg_range_pct - SWING_TARGET_PCT) / SWING_TARGET_PCT)
    return _clamp_score(proximity * 100.0)


def score_momentum(conn: sqlite3.Connection, ticker: str) -> float | None:
    ticker_bars = _fetch_recent_bars(conn, ticker, limit=22)
    spy_bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=22)
    if len(ticker_bars) < 6 or len(spy_bars) < 6:
        return None

    t_closes = [b["close"] for b in ticker_bars]
    s_closes = [b["close"] for b in spy_bars]
    relatives: list[float] = []
    for window in MOMENTUM_WINDOWS:
        t_ret = _return_pct(t_closes, window)
        s_ret = _return_pct(s_closes, window)
        if t_ret is None or s_ret is None:
            continue
        relatives.append(t_ret - s_ret)
    if not relatives:
        return None
    return _score_from_relative(mean(relatives))


def score_relative_strength(conn: sqlite3.Connection, ticker: str) -> float | None:
    ticker_bars = _fetch_recent_bars(conn, ticker, limit=RS_WINDOW + 1)
    spy_bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=RS_WINDOW + 1)
    if len(ticker_bars) < RS_WINDOW + 1 or len(spy_bars) < RS_WINDOW + 1:
        return None
    t_ret = _return_pct([b["close"] for b in ticker_bars], RS_WINDOW)
    s_ret = _return_pct([b["close"] for b in spy_bars], RS_WINDOW)
    if t_ret is None or s_ret is None:
        return None
    return _score_from_relative(t_ret - s_ret)


def score_volume(conn: sqlite3.Connection, ticker: str) -> float | None:
    bars = _fetch_recent_bars(conn, ticker, limit=VOLUME_WINDOW + 1)
    if len(bars) < 2:
        return None
    volumes = [b["volume"] for b in bars]
    latest = volumes[-1]
    history = volumes[:-1]
    if not history:
        return None
    avg_vol = mean(history)
    if avg_vol <= 0:
        return None
    ratio = latest / avg_vol
    return _clamp_score(50.0 + (ratio - 1.0) * 40.0)


def score_dollar_history(
    *,
    dollar_hit_rate_pct: float,
    avg_net_at_high: float,
    net_target: float,
    days_screened: int,
) -> float:
    hit = min(max(dollar_hit_rate_pct, 0.0), 100.0) / 100.0
    avg_ratio = (
        min(avg_net_at_high / net_target, 1.0) if net_target > 0 and avg_net_at_high > 0 else 0.0
    )
    days_factor = min(days_screened / 2.0, 1.0)
    raw = (hit * 55.0) + (avg_ratio * 35.0) + (days_factor * 10.0)
    return _clamp_score(raw)


def score_news_significance(conn: sqlite3.Connection, ticker: str) -> float | None:
    try:
        payload = compute_news_significance(conn, ticker)
    except Exception:
        return None
    return float(payload.get("news_significance", 0))


def score_earnings_events(conn: sqlite3.Connection, ticker: str) -> float | None:
    try:
        payload = compute_news_significance(conn, ticker)
    except Exception:
        return None
    if payload.get("earnings_events"):
        return 100.0
    return 35.0


def compute_factor_scores(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    live_pass: bool,
    near_swing: bool,
    meets_liquidity: bool,
    adv_dollar: float,
    avg_range_pct: float,
    days_screened: int,
    dollar_hit_rate_pct: float,
    avg_net_at_high: float,
    net_target: float,
    period_days: int = 14,
) -> dict[str, float | None]:
    return {
        "market_regime": score_market_regime(conn),
        "technical_setup": score_technical_setup(
            live_pass=live_pass,
            near_swing=near_swing,
            meets_liquidity=meets_liquidity,
            adv_dollar=adv_dollar,
            days_screened=days_screened,
            period_days=period_days,
        ),
        "momentum": score_momentum(conn, ticker),
        "relative_strength": score_relative_strength(conn, ticker),
        "volume": score_volume(conn, ticker),
        "volatility": score_volatility(avg_range_pct),
        "news_significance": score_news_significance(conn, ticker),
        "earnings_events": score_earnings_events(conn, ticker),
        "dollar_history": score_dollar_history(
            dollar_hit_rate_pct=dollar_hit_rate_pct,
            avg_net_at_high=avg_net_at_high,
            net_target=net_target,
            days_screened=days_screened,
        ),
    }


def compute_opportunity_score(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    live_pass: bool,
    near_swing: bool,
    meets_liquidity: bool,
    adv_dollar: float,
    avg_range_pct: float,
    days_screened: int,
    dollar_hit_rate_pct: float,
    avg_net_at_high: float,
    net_target: float,
    period_days: int = 14,
) -> dict:
    factor_scores = compute_factor_scores(
        conn,
        ticker=ticker,
        live_pass=live_pass,
        near_swing=near_swing,
        meets_liquidity=meets_liquidity,
        adv_dollar=adv_dollar,
        avg_range_pct=avg_range_pct,
        days_screened=days_screened,
        dollar_hit_rate_pct=dollar_hit_rate_pct,
        avg_net_at_high=avg_net_at_high,
        net_target=net_target,
        period_days=period_days,
    )
    composite, weights_used = composite_opportunity_score(factor_scores)
    return {
        "opportunity_score": composite,
        "factor_scores": {k: (round(v, 1) if v is not None else None) for k, v in factor_scores.items()},
        "factor_weights_used": weights_used,
        "passes_opportunity_floor": passes_opportunity_floor(composite),
        "opportunity_floor": OPPORTUNITY_FLOOR,
    }


def attach_opportunity_score(
    conn: sqlite3.Connection,
    row: dict,
    *,
    net_target: float,
    period_days: int = 14,
) -> dict:
    """Merge opportunity score fields onto a ranked/screener row dict."""
    opp = compute_opportunity_score(
        conn,
        ticker=row["ticker"],
        live_pass=bool(row.get("live_pass_today")),
        near_swing=bool(row.get("near_swing_target")),
        meets_liquidity=bool(row.get("meets_liquidity")),
        adv_dollar=float(row.get("adv_dollar") or 0),
        avg_range_pct=float(row.get("avg_range_pct") or 0),
        days_screened=int(row.get("days_screened") or 0),
        dollar_hit_rate_pct=float(row.get("dollar_hit_rate_pct") or 0),
        avg_net_at_high=float(row.get("avg_net_at_high") or 0),
        net_target=net_target,
        period_days=period_days,
    )
    return {**row, **opp}
