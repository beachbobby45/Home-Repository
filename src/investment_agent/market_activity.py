"""Market Activity Engine — day-level TRADE / NO TRADE score (Phase 1B Inc 12).

Computes a 0–100 composite from index direction, volume, volatility, momentum,
sector participation, and macro news. Breadth and VWAP are n/a on free tier v0;
weights renormalize across available components.

See docs/PHASE1B_MARKET_ACTIVITY.md.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from zoneinfo import ZoneInfo

from investment_agent.account import latest_vix
from investment_agent.opportunity_score import composite_opportunity_score
from investment_agent.regime import REGIME_SYMBOLS, intraday_change_pct
from investment_agent.quote_snapshots import (
    SNAPSHOT_SLOTS,
    get_snapshots_for_tickers,
    snapshot_slot_for_time,
    today_et_str,
)

ET = ZoneInfo("America/New_York")
SPY_BENCHMARK = "SPY"
MOMENTUM_WINDOWS = (5, 10, 20)
RS_WINDOW = 20
VOLUME_WINDOW = 20
SECTOR_ETFS = ("XLK", "XLF", "XLE", "XLV", "XLI")

# Nominal weights; breadth + vwap excluded on free-tier v0.
MARKET_ACTIVITY_WEIGHTS: dict[str, float] = {
    "market_direction": 20.0,
    "market_volume": 15.0,
    "market_breadth": 15.0,  # n/a v0
    "volatility": 10.0,
    "momentum": 15.0,
    "sector_participation": 10.0,
    "vwap_trend": 10.0,  # n/a v0
    "news_catalysts": 5.0,
}

V0_ACTIVE_WEIGHTS = {
    k: v for k, v in MARKET_ACTIVITY_WEIGHTS.items() if k not in ("market_breadth", "vwap_trend")
}

# Day gate bands (calibrated Aug 2026 — 75 blocked all 158 YTD sessions).
TRADE_MIN = 60  # Minimum score to allow new entries (Average band)
GO_SESSION_MIN = 70  # Session chip GO vs CAUTION
ABOVE_AVERAGE_MIN = GO_SESSION_MIN
EXCEPTIONAL_MIN = 80
AVERAGE_MIN = TRADE_MIN
BELOW_AVERAGE_MIN = 40
FLIP_EXIT_MIN = 55  # Two consecutive reads below → exit alert

MACRO_POSITIVE = re.compile(
    r"\b(rate cut|cuts rates|dovish|soft landing|beat estimates|gdp growth)\b",
    re.IGNORECASE,
)
MACRO_NEGATIVE = re.compile(
    r"\b(rate hike|hikes rates|hawkish|recession|inflation surge|miss estimates|"
    r"layoffs|bank failure|default|downgrade)\b",
    re.IGNORECASE,
)
MACRO_ANY = re.compile(
    r"\b(fed|fomc|cpi|inflation|jobs report|nonfarm|gdp|treasury|powell)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MarketActivityBand:
    key: str
    label: str
    min_score: int
    allow_trade: bool


BANDS: tuple[MarketActivityBand, ...] = (
    MarketActivityBand("exceptional", "Exceptional", EXCEPTIONAL_MIN, True),
    MarketActivityBand("above_average", "Above average", ABOVE_AVERAGE_MIN, True),
    MarketActivityBand("average", "Average", AVERAGE_MIN, True),
    MarketActivityBand("below_average", "Below average", BELOW_AVERAGE_MIN, False),
    MarketActivityBand("negative", "Negative", 0, False),
)


def now_et() -> datetime:
    return datetime.now(ET)


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def _score_from_relative(relative_pct: float, *, scale: float = 2.0) -> float:
    return _clamp(50.0 + (relative_pct / scale) * 50.0)


def _fetch_recent_bars(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    limit: int = 22,
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


def band_for_score(score: int) -> MarketActivityBand:
    for band in BANDS:
        if score >= band.min_score:
            return band
    return BANDS[-1]


def score_market_direction(index_changes: dict[str, float]) -> float | None:
    if not index_changes:
        return None
    avg_change = mean(index_changes.values())
    return _score_from_relative(avg_change, scale=2.0)


def score_market_volume(conn: sqlite3.Connection) -> float | None:
    bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=VOLUME_WINDOW + 1)
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
    return _clamp(50.0 + (ratio - 1.0) * 35.0)


def score_volatility_component(vix: float | None) -> float | None:
    if vix is None:
        return None
    if vix <= 14:
        return 90.0
    if vix <= 18:
        return 80.0
    if vix <= 22:
        return 65.0
    if vix <= 28:
        return 45.0
    return 25.0


def score_index_momentum(conn: sqlite3.Connection) -> float | None:
    bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=22)
    if len(bars) < 6:
        return None
    closes = [b["close"] for b in bars]
    returns: list[float] = []
    for window in MOMENTUM_WINDOWS:
        ret = _return_pct(closes, window)
        if ret is not None:
            returns.append(ret)
    if not returns:
        return None
    return _score_from_relative(mean(returns), scale=4.0)


def score_sector_participation(conn: sqlite3.Connection) -> float | None:
    spy_bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=RS_WINDOW + 1)
    if len(spy_bars) < RS_WINDOW + 1:
        return None
    spy_ret = _return_pct([b["close"] for b in spy_bars], RS_WINDOW)
    if spy_ret is None:
        return None

    rs_scores: list[float] = []
    for etf in SECTOR_ETFS:
        etf_bars = _fetch_recent_bars(conn, etf, limit=RS_WINDOW + 1)
        if len(etf_bars) < RS_WINDOW + 1:
            continue
        etf_ret = _return_pct([b["close"] for b in etf_bars], RS_WINDOW)
        if etf_ret is None:
            continue
        rs_scores.append(_score_from_relative(etf_ret - spy_ret, scale=3.0))
    if not rs_scores:
        return None
    return _clamp(mean(rs_scores))


def score_news_catalysts(conn: sqlite3.Connection) -> float | None:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(microsecond=0).isoformat()
    rows = conn.execute(
        """
        SELECT headline, summary
        FROM news_headlines
        WHERE published_at >= ?
        ORDER BY published_at DESC
        LIMIT 100
        """,
        (since,),
    ).fetchall()
    if not rows:
        return 70.0

    macro_hits = 0
    negative = 0
    positive = 0
    for row in rows:
        text = f"{row['headline']} {row['summary'] or ''}"
        if not MACRO_ANY.search(text):
            continue
        macro_hits += 1
        if MACRO_NEGATIVE.search(text):
            negative += 1
        elif MACRO_POSITIVE.search(text):
            positive += 1

    if negative > 0:
        return _clamp(35.0 - negative * 5.0)
    if positive > 0:
        return _clamp(75.0 + positive * 5.0)
    if macro_hits > 0:
        return 55.0
    return 70.0


def spy_20d_return_pct(conn: sqlite3.Connection) -> float | None:
    bars = _fetch_recent_bars(conn, SPY_BENCHMARK, limit=RS_WINDOW + 1)
    if len(bars) < RS_WINDOW + 1:
        return None
    return _return_pct([b["close"] for b in bars], RS_WINDOW)


def _preferred_snapshot_slot(when: datetime) -> str | None:
    slot = snapshot_slot_for_time(when)
    if slot:
        return slot
    t = when.time()
    if t.hour >= 10 or (t.hour == 9 and t.minute >= 45):
        return "plus_15m"
    if t.hour > 9 or (t.hour == 9 and t.minute >= 30):
        return "at_open"
    return "pre_market"


def _snapshot_slot_order(preferred: str | None) -> list[str]:
    if preferred and preferred in SNAPSHOT_SLOTS:
        idx = SNAPSHOT_SLOTS.index(preferred)
        return list(reversed(SNAPSHOT_SLOTS[: idx + 1]))
    return list(reversed(SNAPSHOT_SLOTS))


def _resolve_index_quotes(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    when: datetime,
) -> tuple[dict[str, dict], str | None]:
    """Return index quote rows and the snapshot slot used (if any)."""
    preferred = _preferred_snapshot_slot(when)
    snaps = get_snapshots_for_tickers(
        conn, list(REGIME_SYMBOLS), session_date_et=session_date_et
    )
    for slot in _snapshot_slot_order(preferred):
        quotes: dict[str, dict] = {}
        for sym in REGIME_SYMBOLS:
            row = (snaps.get(sym) or {}).get(slot)
            if row and row.get("price"):
                quotes[sym] = row
        if len(quotes) == len(REGIME_SYMBOLS):
            return quotes, slot

    placeholders = ",".join("?" for _ in REGIME_SYMBOLS)
    rows = conn.execute(
        f"""
        SELECT q.ticker, q.price, q.open, q.high, q.low, q.prev_close, q.captured_at
        FROM quotes q
        INNER JOIN (
          SELECT ticker, MAX(captured_at) AS max_at
          FROM quotes
          WHERE ticker IN ({placeholders})
          GROUP BY ticker
        ) latest ON q.ticker = latest.ticker AND q.captured_at = latest.max_at
        """,
        list(REGIME_SYMBOLS),
    ).fetchall()
    live = {
        row["ticker"]: {
            "price": float(row["price"]),
            "open": float(row["open"]) if row["open"] is not None else None,
            "high": float(row["high"]) if row["high"] is not None else None,
            "low": float(row["low"]) if row["low"] is not None else None,
            "prev_close": float(row["prev_close"]) if row["prev_close"] is not None else None,
            "captured_at": row["captured_at"],
        }
        for row in rows
    }
    if len(live) == len(REGIME_SYMBOLS):
        return live, None
    return live, None


def _index_changes(index_quotes: dict[str, dict]) -> dict[str, float]:
    changes: dict[str, float] = {}
    for sym in REGIME_SYMBOLS:
        row = index_quotes.get(sym)
        if not row or row.get("price") is None:
            continue
        changes[sym] = intraday_change_pct(
            float(row["price"]),
            row.get("open"),
            row.get("prev_close"),
        )
    return changes


def evaluate_market_activity(
    conn: sqlite3.Connection,
    *,
    when: datetime | None = None,
    persist: bool = False,
) -> dict:
    """Compute market activity score, band, and trade authorization for the session."""
    dt = when or now_et()
    session_date = today_et_str(dt)
    index_quotes, snapshot_slot = _resolve_index_quotes(
        conn, session_date_et=session_date, when=dt
    )
    index_changes = _index_changes(index_quotes)

    factor_scores: dict[str, float | None] = {
        "market_direction": score_market_direction(index_changes),
        "market_volume": score_market_volume(conn),
        "volatility": score_volatility_component(latest_vix(conn)),
        "momentum": score_index_momentum(conn),
        "sector_participation": score_sector_participation(conn),
        "news_catalysts": score_news_catalysts(conn),
    }
    score, used_weights = composite_opportunity_score(factor_scores, weights=V0_ACTIVE_WEIGHTS)
    band = band_for_score(score)
    spy_20d = spy_20d_return_pct(conn)
    bull_gate_ok = spy_20d is not None and spy_20d > 0
    allow_trade = band.allow_trade and bull_gate_ok

    exit_alert = False
    flip_reason: str | None = None
    if score < BELOW_AVERAGE_MIN:
        exit_alert = True
        flip_reason = "Market Activity in Negative band — exit at market if holding"
    elif score < FLIP_EXIT_MIN:
        recent = list_recent_evaluations(conn, session_date, limit=1)
        if recent and recent[0]["score"] < FLIP_EXIT_MIN:
            exit_alert = True
            flip_reason = (
                f"Two consecutive reads below {FLIP_EXIT_MIN} — exit at market if holding"
            )

    if persist:
        save_market_activity_evaluation(
            conn,
            session_date_et=session_date,
            captured_at=dt.replace(microsecond=0).isoformat(),
            slot=snapshot_slot or snapshot_slot_for_time(dt),
            score=score,
            band=band.key,
            allow_trade=allow_trade,
            bull_gate_ok=bull_gate_ok,
            exit_alert=exit_alert,
            components=factor_scores,
            summary=_build_summary(score, band, bull_gate_ok, spy_20d, index_changes),
        )
        if exit_alert and not flip_reason:
            flip_reason = "Market Activity flip — exit at market if holding"

    components_out = {
        name: round(val, 1) if val is not None else None for name, val in factor_scores.items()
    }
    return {
        "session_date_et": session_date,
        "captured_at": dt.replace(microsecond=0).isoformat(),
        "snapshot_slot": snapshot_slot,
        "score": score,
        "band": band.key,
        "band_label": band.label,
        "allow_trade": allow_trade,
        "bull_gate_ok": bull_gate_ok,
        "spy_20d_return_pct": round(spy_20d, 3) if spy_20d is not None else None,
        "index_changes": {k: round(v, 3) for k, v in index_changes.items()},
        "components": components_out,
        "weights_used": used_weights,
        "exit_alert": exit_alert,
        "flip_reason": flip_reason,
        "summary": _build_summary(score, band, bull_gate_ok, spy_20d, index_changes),
        "authoritative": snapshot_slot == "plus_15m" or (
            snapshot_slot is None and dt.time().hour >= 9 and dt.minute >= 45
        ),
    }


def _build_summary(
    score: int,
    band: MarketActivityBand,
    bull_gate_ok: bool,
    spy_20d: float | None,
    index_changes: dict[str, float],
) -> str:
    parts = [f"Market Activity {score}/100 — {band.label}"]
    if index_changes:
        idx = ", ".join(f"{sym} {index_changes[sym]:+.2f}%" for sym in REGIME_SYMBOLS if sym in index_changes)
        if idx:
            parts.append(idx)
    if not bull_gate_ok:
        ret = f"{spy_20d:+.2f}%" if spy_20d is not None else "n/a"
        parts.append(f"Bull gate off (SPY 20d {ret}) — NO TRADE")
    elif not band.allow_trade:
        parts.append("NO TRADE today")
    elif score < GO_SESSION_MIN:
        parts.append("CAUTION — trade only if #1 confirms (≥70)")
    return " · ".join(parts)


def save_market_activity_evaluation(
    conn: sqlite3.Connection,
    *,
    session_date_et: str,
    captured_at: str,
    slot: str | None,
    score: int,
    band: str,
    allow_trade: bool,
    bull_gate_ok: bool,
    exit_alert: bool,
    components: dict[str, float | None],
    summary: str,
) -> None:
    conn.execute(
        """
        INSERT INTO market_activity_evaluations
          (session_date_et, captured_at, slot, score, band, allow_trade,
           bull_gate_ok, exit_alert, components_json, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_date_et,
            captured_at,
            slot,
            score,
            band,
            1 if allow_trade else 0,
            1 if bull_gate_ok else 0,
            1 if exit_alert else 0,
            json.dumps({k: v for k, v in components.items() if v is not None}),
            summary,
        ),
    )


def list_recent_evaluations(
    conn: sqlite3.Connection,
    session_date_et: str,
    *,
    limit: int = 5,
) -> list[dict]:
    rows = conn.execute(
        """
        SELECT captured_at, slot, score, band, allow_trade, bull_gate_ok, exit_alert, summary
        FROM market_activity_evaluations
        WHERE session_date_et = ?
        ORDER BY captured_at DESC
        LIMIT ?
        """,
        (session_date_et, limit),
    ).fetchall()
    return [
        {
            "captured_at": row["captured_at"],
            "slot": row["slot"],
            "score": int(row["score"]),
            "band": row["band"],
            "allow_trade": bool(row["allow_trade"]),
            "bull_gate_ok": bool(row["bull_gate_ok"]),
            "exit_alert": bool(row["exit_alert"]),
            "summary": row["summary"],
        }
        for row in rows
    ]


def market_activity_to_dict(result: dict) -> dict:
    """Stable API payload for dashboard and tests."""
    return {
        "session_date_et": result["session_date_et"],
        "captured_at": result["captured_at"],
        "snapshot_slot": result.get("snapshot_slot"),
        "score": result["score"],
        "band": result["band"],
        "band_label": result["band_label"],
        "allow_trade": result["allow_trade"],
        "bull_gate_ok": result["bull_gate_ok"],
        "spy_20d_return_pct": result.get("spy_20d_return_pct"),
        "index_changes": result.get("index_changes") or {},
        "components": result.get("components") or {},
        "exit_alert": result.get("exit_alert", False),
        "flip_reason": result.get("flip_reason"),
        "summary": result.get("summary"),
        "authoritative": result.get("authoritative", False),
    }
