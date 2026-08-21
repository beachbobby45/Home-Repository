"""Opening Drive — early-entry scoring for ranked picks (9:35–9:45 ET).

Scores whether #1 is holding above the open with modest gap and RS vs SPY,
so a selective early entry is allowed before the default 10:00 ET gate.

See docs/PHASE1B_MARKET_ACTIVITY.md and opening-drive backtest script.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, time
from zoneinfo import ZoneInfo

from investment_agent.market_activity import GO_SESSION_MIN
from investment_agent.opportunity_score import composite_opportunity_score
from investment_agent.regime import REGIME_SYMBOLS, intraday_change_pct
from investment_agent.tradability import (
    OPENING_DRIVE_MAX_CHASE_ABOVE_OPEN_PCT,
    assess_entry_tradability,
)

ET = ZoneInfo("America/New_York")

OPENING_DRIVE_PASS_MIN = 75
OPENING_DRIVE_WATCH_MIN = 60
OPENING_DRIVE_START = time(9, 35)
OPENING_DRIVE_END = time(9, 46)

OPENING_DRIVE_WEIGHTS: dict[str, float] = {
    "hold_above_open": 25.0,
    "gap_band": 20.0,
    "relative_strength": 20.0,
    "no_fade": 15.0,
    "tradability": 20.0,
}

GAP_SWEET_MIN = 0.15
GAP_SWEET_MAX = 0.95
HOLD_BUFFER_PCT = 0.05
FADE_MAX_BELOW_OPEN_PCT = 0.20


def now_et() -> datetime:
    return datetime.now(ET)


def opening_drive_window_active(when: datetime | None = None) -> bool:
    dt = when or now_et()
    if dt.weekday() >= 5:
        return False
    t = dt.time()
    return OPENING_DRIVE_START <= t < OPENING_DRIVE_END


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _score_hold_above_open(price: float, open_px: float | None) -> float | None:
    if not open_px or open_px <= 0:
        return None
    buffer_px = open_px * (1 - HOLD_BUFFER_PCT / 100.0)
    if price >= open_px:
        excess = ((price - open_px) / open_px) * 100.0
        return _clamp(55.0 + excess * 25.0)
    if price >= buffer_px:
        return 45.0
    return _clamp(30.0 + ((price - buffer_px) / (open_px - buffer_px)) * 15.0)


def _score_gap_band(gap_pct: float | None) -> float | None:
    if gap_pct is None:
        return None
    if GAP_SWEET_MIN <= gap_pct <= GAP_SWEET_MAX:
        mid = (GAP_SWEET_MIN + GAP_SWEET_MAX) / 2
        dist = abs(gap_pct - mid)
        return _clamp(95.0 - dist * 35.0)
    if 0 <= gap_pct < GAP_SWEET_MIN:
        return _clamp(40.0 + (gap_pct / GAP_SWEET_MIN) * 35.0)
    if gap_pct < 0:
        return _clamp(35.0 + gap_pct * 5.0)
    if gap_pct <= 1.5:
        return _clamp(55.0 - (gap_pct - GAP_SWEET_MAX) * 30.0)
    return 25.0


def _score_relative_strength(stock_change: float | None, spy_change: float | None) -> float | None:
    if stock_change is None or spy_change is None:
        return None
    return _clamp(50.0 + (stock_change - spy_change) * 25.0)


def _score_no_fade(price: float, open_px: float | None, low: float | None) -> float | None:
    if not open_px or open_px <= 0:
        return None
    ref = low if low is not None else price
    drop_pct = ((open_px - ref) / open_px) * 100.0
    if drop_pct <= 0:
        return 90.0
    if drop_pct <= FADE_MAX_BELOW_OPEN_PCT:
        return _clamp(75.0 - drop_pct * 80.0)
    return _clamp(35.0 - (drop_pct - FADE_MAX_BELOW_OPEN_PCT) * 10.0)


def _gap_at_open_pct(quote: dict) -> float | None:
    open_px = quote.get("open")
    prev = quote.get("prev_close")
    if not open_px or not prev or prev <= 0:
        return None
    return ((float(open_px) - float(prev)) / float(prev)) * 100.0


def _tradability_score(
    *,
    quote: dict,
    entry_price: float,
    deploy_dollar: float,
    net_target: float,
    conn: sqlite3.Connection | None,
    ticker: str,
    block_new_longs: bool,
) -> float | None:
    result = assess_entry_tradability(
        quote=quote,
        entry_price=entry_price,
        deploy_dollar=deploy_dollar,
        net_target=net_target,
        conn=conn,
        ticker=ticker,
        block_new_longs=block_new_longs,
        max_chase_above_open_pct=OPENING_DRIVE_MAX_CHASE_ABOVE_OPEN_PCT,
    )
    verdict = result.get("verdict")
    if verdict == "TRADABLE":
        return 90.0
    if verdict == "CAUTION":
        return 65.0
    if verdict == "UNKNOWN":
        return None
    return 30.0


def evaluate_opening_drive(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    quote: dict | None,
    spy_quote: dict | None,
    market_activity: dict,
    deploy_dollar: float,
    net_target: float,
    block_new_longs: bool = False,
    when: datetime | None = None,
) -> dict:
    """Score opening-drive continuation for one ticker."""
    dt = when or now_et()
    sym = ticker.upper()
    active = opening_drive_window_active(dt)
    day_allows = bool(market_activity.get("allow_trade"))

    if not quote or quote.get("price") is None:
        return _result(
            sym,
            score=0,
            verdict="pending",
            active=active,
            day_allows=day_allows,
            summary=f"{sym} — no live quote for opening drive",
            eligible_early_entry=False,
            components={},
        )

    price = float(quote["price"])
    open_px = quote.get("open")
    open_px_f = float(open_px) if open_px else None
    gap_pct = _gap_at_open_pct(quote)
    stock_change = intraday_change_pct(price, quote.get("open"), quote.get("prev_close"))
    spy_change = None
    if spy_quote and spy_quote.get("price") is not None:
        spy_change = intraday_change_pct(
            float(spy_quote["price"]),
            spy_quote.get("open"),
            spy_quote.get("prev_close"),
        )

    entry_price = price
    if open_px_f and open_px_f > 0:
        entry_price = min(price, open_px_f * (1 + OPENING_DRIVE_MAX_CHASE_ABOVE_OPEN_PCT / 100.0))

    factor_scores: dict[str, float | None] = {
        "hold_above_open": _score_hold_above_open(price, open_px_f),
        "gap_band": _score_gap_band(gap_pct),
        "relative_strength": _score_relative_strength(stock_change, spy_change),
        "no_fade": _score_no_fade(price, open_px_f, quote.get("low")),
        "tradability": _tradability_score(
            quote=quote,
            entry_price=entry_price,
            deploy_dollar=deploy_dollar,
            net_target=net_target,
            conn=conn,
            ticker=sym,
            block_new_longs=block_new_longs,
        ),
    }
    score, used_weights = composite_opportunity_score(factor_scores, weights=OPENING_DRIVE_WEIGHTS)

    if not active:
        verdict = "inactive"
        summary = f"{sym} {score}/100 — opening drive window 9:35–9:45 ET"
        eligible = False
    elif not day_allows:
        verdict = "blocked"
        summary = f"{sym} {score}/100 — day NO TRADE (opening drive informational)"
        eligible = False
    elif score >= OPENING_DRIVE_PASS_MIN:
        verdict = "pass"
        summary = f"{sym} {score}/100 — OPEN DRIVE PASS (early entry eligible)"
        eligible = True
    elif score >= OPENING_DRIVE_WATCH_MIN:
        verdict = "watch"
        summary = f"{sym} {score}/100 — OPEN WATCH (wait for 10:00 unless strengthens)"
        eligible = False
    else:
        verdict = "fade"
        summary = f"{sym} {score}/100 — OPEN FADE (use 10:00 gate or skip)"
        eligible = False

    components_out = {
        name: round(val, 1) if val is not None else None for name, val in factor_scores.items()
    }
    return _result(
        sym,
        score=score,
        verdict=verdict,
        active=active,
        day_allows=day_allows,
        summary=summary,
        eligible_early_entry=eligible,
        components=components_out,
        weights_used=used_weights,
        gap_at_open_pct=round(gap_pct, 3) if gap_pct is not None else None,
        change_vs_open_pct=round(stock_change, 3) if stock_change is not None else None,
        rs_vs_spy_pct=round(stock_change - spy_change, 3)
        if stock_change is not None and spy_change is not None
        else None,
        entry_price=round(entry_price, 2),
    )


def evaluate_top_pick_opening_drive(
    conn: sqlite3.Connection,
    *,
    pick: dict | None,
    quotes: dict[str, dict],
    market_activity: dict,
    deploy_dollar: float,
    net_target: float,
    block_new_longs: bool = False,
    when: datetime | None = None,
) -> dict | None:
    if not pick or not pick.get("ticker"):
        return None
    ticker = pick["ticker"].upper()
    quote = quotes.get(ticker)
    spy_quote = quotes.get("SPY")
    return evaluate_opening_drive(
        conn,
        ticker,
        quote=quote,
        spy_quote=spy_quote,
        market_activity=market_activity,
        deploy_dollar=deploy_dollar,
        net_target=net_target,
        block_new_longs=block_new_longs,
        when=when,
    )


def opening_drive_to_dict(result: dict | None) -> dict | None:
    if not result:
        return None
    return {
        "ticker": result.get("ticker"),
        "score": result.get("score"),
        "verdict": result.get("verdict"),
        "verdict_label": _verdict_label(result.get("verdict")),
        "active": result.get("active"),
        "day_allows": result.get("day_allows"),
        "eligible_early_entry": result.get("eligible_early_entry"),
        "summary": result.get("summary"),
        "components": result.get("components") or {},
        "gap_at_open_pct": result.get("gap_at_open_pct"),
        "change_vs_open_pct": result.get("change_vs_open_pct"),
        "rs_vs_spy_pct": result.get("rs_vs_spy_pct"),
        "entry_price": result.get("entry_price"),
        "window_et": "9:35–9:45",
        "pass_min": OPENING_DRIVE_PASS_MIN,
        "watch_min": OPENING_DRIVE_WATCH_MIN,
    }


def _verdict_label(verdict: str | None) -> str:
    return {
        "pass": "OPEN DRIVE PASS",
        "watch": "OPEN WATCH",
        "fade": "OPEN FADE",
        "blocked": "DAY BLOCKED",
        "inactive": "NOT YET ACTIVE",
        "pending": "PENDING",
    }.get(verdict or "", verdict or "")


def _result(
    ticker: str,
    *,
    score: int,
    verdict: str,
    active: bool,
    day_allows: bool,
    summary: str,
    eligible_early_entry: bool,
    components: dict,
    weights_used: dict | None = None,
    gap_at_open_pct: float | None = None,
    change_vs_open_pct: float | None = None,
    rs_vs_spy_pct: float | None = None,
    entry_price: float | None = None,
) -> dict:
    return {
        "ticker": ticker,
        "score": int(score),
        "verdict": verdict,
        "active": active,
        "day_allows": day_allows,
        "eligible_early_entry": eligible_early_entry,
        "summary": summary,
        "components": components,
        "weights_used": weights_used or {},
        "gap_at_open_pct": gap_at_open_pct,
        "change_vs_open_pct": change_vs_open_pct,
        "rs_vs_spy_pct": rs_vs_spy_pct,
        "entry_price": entry_price,
    }
