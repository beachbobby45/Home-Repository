"""Top-3 "best tradable now" soft scorer for paper / armed propose.

Soft score (not hard filters): every candidate stays eligible; metrics nudge rank.
Defaults (Tony-approved 2026-10-22):
  - Shortlist: prep ranks #1–#3
  - Trend: last price > 30d SMA or > session VWAP (soft bonus)
  - Volume: last 6×5m bars rising vs prior 20-bar avg volume
  - Short MA: 9×5m SMA; pullback holds above it with bounce volume expansion
  - Composite: limit reachability + MA + volume + pullback; ties → better prep rank
  - Still one name/day
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Sequence
from zoneinfo import ZoneInfo

from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE

ET = ZoneInfo("America/New_York")

# Frozen defaults — change only with an explicit product decision.
TOP_N = 3
DAILY_MA_BARS = 30
SHORT_MA_BARS = 9
VOLUME_LOOKBACK_N = 6
VOLUME_AVG_BARS = 20

WEIGHT_REACHABILITY = 0.35
WEIGHT_TREND_MA = 0.25
WEIGHT_VOLUME = 0.20
WEIGHT_PULLBACK = 0.20


@dataclass(frozen=True)
class MetricScores:
    reachability: float
    trend_ma: float
    volume: float
    pullback: float
    above_30d_ma: bool | None
    above_vwap: bool | None
    volume_expanding: bool | None
    pullback_holds: bool | None
    last_price: float | None
    sma_30d: float | None
    vwap: float | None
    short_ma: float | None
    detail: str = ""


@dataclass
class CandidateScore:
    rank: int
    ticker: str
    composite: float
    metrics: MetricScores
    limit_buy: float
    limit_sell: float
    stop: float
    shares: int
    deploy: float
    avg_range_pct: float | None = None
    source: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "ticker": self.ticker,
            "composite": round(self.composite, 4),
            "metrics": asdict(self.metrics),
            "limit_buy": self.limit_buy,
            "limit_sell": self.limit_sell,
            "stop": self.stop,
            "shares": self.shares,
            "deploy": self.deploy,
            "avg_range_pct": self.avg_range_pct,
            "source": self.source,
        }


@dataclass
class SelectionResult:
    winner: CandidateScore | None
    scored: list[CandidateScore]
    mode: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "reason": self.reason,
            "winner": self.winner.to_dict() if self.winner else None,
            "scored": [c.to_dict() for c in self.scored],
        }


def _bar_time_et(bar: dict) -> datetime | None:
    ts = bar.get("ts")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def _closes(bars: Sequence[dict], key: str = "close") -> list[float]:
    out: list[float] = []
    for b in bars:
        try:
            v = float(b[key])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            out.append(v)
    return out


def sma(values: Sequence[float], window: int) -> float | None:
    if window <= 0 or len(values) < window:
        return None
    chunk = values[-window:]
    return sum(chunk) / window


def session_vwap(bars_5m: Sequence[dict]) -> float | None:
    num = 0.0
    den = 0.0
    for b in bars_5m:
        try:
            h, l, c = float(b["high"]), float(b["low"]), float(b["close"])
            vol = float(b.get("volume") or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if c <= 0 or vol <= 0:
            continue
        typical = (h + l + c) / 3.0
        num += typical * vol
        den += vol
    if den <= 0:
        return None
    return num / den


def score_trend_ma(
    *,
    last_price: float | None,
    sma_30d: float | None,
    vwap: float | None,
) -> tuple[float, bool | None, bool | None]:
    """Soft 0–1: prefer price above 30d SMA or session VWAP."""
    if last_price is None or last_price <= 0:
        return 0.5, None, None
    above_30 = None if sma_30d is None else last_price > sma_30d
    above_v = None if vwap is None else last_price > vwap
    if above_30 is True or above_v is True:
        both = above_30 is True and above_v is True
        return (1.0 if both else 0.85), above_30, above_v
    if above_30 is False and above_v is False:
        return 0.15, above_30, above_v
    if above_30 is False or above_v is False:
        return 0.35, above_30, above_v
    return 0.5, above_30, above_v


def score_volume_expansion(bars_5m: Sequence[dict]) -> tuple[float, bool | None]:
    """Last N bars' avg volume vs prior VOLUME_AVG_BARS average."""
    vols: list[float] = []
    for b in bars_5m:
        try:
            vols.append(max(0.0, float(b.get("volume") or 0)))
        except (TypeError, ValueError):
            vols.append(0.0)
    need = VOLUME_LOOKBACK_N + VOLUME_AVG_BARS
    if len(vols) < need:
        if len(vols) < VOLUME_LOOKBACK_N + 2:
            return 0.5, None
        baseline = vols[: -VOLUME_LOOKBACK_N]
        recent = vols[-VOLUME_LOOKBACK_N:]
    else:
        baseline = vols[-(need):-VOLUME_LOOKBACK_N]
        recent = vols[-VOLUME_LOOKBACK_N:]
    base_avg = sum(baseline) / len(baseline) if baseline else 0.0
    recent_avg = sum(recent) / len(recent) if recent else 0.0
    if base_avg <= 0:
        return 0.5, None
    ratio = recent_avg / base_avg
    expanding = ratio > 1.0
    # Map ratio ~0.5→0, 1.0→0.55, 1.5+→1.0
    score = max(0.0, min(1.0, (ratio - 0.5) / 1.0))
    return score, expanding


def score_pullback_quality(bars_5m: Sequence[dict]) -> tuple[float, bool | None, float | None]:
    """Prefer pullback that holds above short MA with volume expanding on bounce."""
    if len(bars_5m) < SHORT_MA_BARS + 3:
        return 0.5, None, None
    closes = _closes(bars_5m)
    short = sma(closes, SHORT_MA_BARS)
    if short is None:
        return 0.5, None, None

    vols = [float(b.get("volume") or 0) for b in bars_5m]
    vol_avg = (
        sum(vols[-(VOLUME_AVG_BARS + 1) : -1]) / VOLUME_AVG_BARS
        if len(vols) > VOLUME_AVG_BARS
        else (sum(vols[:-1]) / max(len(vols) - 1, 1))
    )
    window = bars_5m[-(SHORT_MA_BARS + 3) :]
    lows = [float(b["low"]) for b in window]
    min_i = lows.index(min(lows))
    bounce = window[min_i:]
    if len(bounce) < 2:
        # Still above MA is mildly positive
        last = closes[-1]
        holds = last >= short
        return (0.65 if holds else 0.35), holds, short

    pullback_low = float(bounce[0]["low"])
    holds = pullback_low >= short * 0.998  # tiny tolerance
    bounce_bar = bounce[-1]
    bounce_vol = float(bounce_bar.get("volume") or 0)
    vol_ok = bounce_vol > vol_avg if vol_avg > 0 else None
    last_close = float(bounce_bar["close"])
    reclaim = last_close >= short

    if holds and vol_ok and reclaim:
        return 1.0, True, short
    if holds and reclaim:
        return 0.75, True, short
    if reclaim:
        return 0.55, holds, short
    if holds:
        return 0.40, True, short
    return 0.20, False, short


def score_limit_reachability(
    bars_5m: Sequence[dict],
    *,
    limit_buy: float,
    as_of_et: datetime | None = None,
) -> float:
    """Soft 0–1: already traded through limit, or close enough vs session path."""
    if limit_buy <= 0:
        return 0.0
    bars = list(bars_5m)
    if as_of_et is not None:
        clipped: list[dict] = []
        for b in bars:
            t = _bar_time_et(b)
            if t is not None and t <= as_of_et:
                clipped.append(b)
        bars = clipped
    if not bars:
        return 0.5  # neutral pre-open / no data

    session_low = None
    hit = False
    for b in bars:
        t = _bar_time_et(b)
        if t is not None and t.timetz().replace(tzinfo=None) > LIMIT_FILL_DEADLINE:
            break
        try:
            low = float(b["low"])
        except (KeyError, TypeError, ValueError):
            continue
        if session_low is None or low < session_low:
            session_low = low
        # trade_through style: strict breach preferred
        if low < limit_buy:
            hit = True
    if hit:
        return 1.0
    if session_low is None:
        return 0.5
    # Distance of session low above limit as fraction of limit
    gap_pct = (session_low - limit_buy) / limit_buy
    if gap_pct <= 0:
        return 1.0
    # Within 0.5% → high; 2%+ → low
    if gap_pct >= 0.02:
        return max(0.05, 0.25 - (gap_pct - 0.02) * 2)
    return max(0.25, 1.0 - (gap_pct / 0.02) * 0.75)


def score_candidate(
    *,
    rank: int,
    ticker: str,
    limit_buy: float,
    limit_sell: float,
    stop: float,
    shares: int,
    deploy: float,
    bars_5m: Sequence[dict],
    daily_bars: Sequence[dict],
    avg_range_pct: float | None = None,
    source: str | None = None,
    as_of_et: datetime | None = None,
    raw: dict[str, Any] | None = None,
) -> CandidateScore:
    daily_closes = _closes(daily_bars)
    sma_30 = sma(daily_closes, DAILY_MA_BARS)
    vwap = session_vwap(bars_5m)
    last_price = None
    if bars_5m:
        try:
            last_price = float(bars_5m[-1]["close"])
        except (KeyError, TypeError, ValueError):
            last_price = None
    if last_price is None and daily_closes:
        last_price = daily_closes[-1]

    short_ma = sma(_closes(bars_5m), SHORT_MA_BARS)
    reach = score_limit_reachability(bars_5m, limit_buy=limit_buy, as_of_et=as_of_et)
    trend, above_30, above_v = score_trend_ma(
        last_price=last_price, sma_30d=sma_30, vwap=vwap
    )
    vol_score, expanding = score_volume_expansion(bars_5m)
    pull_score, holds, short = score_pullback_quality(bars_5m)
    if short is not None:
        short_ma = short

    composite = (
        WEIGHT_REACHABILITY * reach
        + WEIGHT_TREND_MA * trend
        + WEIGHT_VOLUME * vol_score
        + WEIGHT_PULLBACK * pull_score
    )
    detail = (
        f"reach={reach:.2f} trend={trend:.2f} vol={vol_score:.2f} "
        f"pull={pull_score:.2f} → {composite:.3f}"
    )
    metrics = MetricScores(
        reachability=reach,
        trend_ma=trend,
        volume=vol_score,
        pullback=pull_score,
        above_30d_ma=above_30,
        above_vwap=above_v,
        volume_expanding=expanding,
        pullback_holds=holds,
        last_price=last_price,
        sma_30d=sma_30,
        vwap=vwap,
        short_ma=short_ma,
        detail=detail,
    )
    return CandidateScore(
        rank=rank,
        ticker=ticker.upper(),
        composite=composite,
        metrics=metrics,
        limit_buy=limit_buy,
        limit_sell=limit_sell,
        stop=stop,
        shares=shares,
        deploy=deploy,
        avg_range_pct=avg_range_pct,
        source=source,
        raw=raw or {},
    )


def select_best_tradable(
    candidates: Sequence[dict[str, Any]],
    *,
    bars_5m_by_ticker: dict[str, Sequence[dict]],
    daily_by_ticker: dict[str, Sequence[dict]],
    as_of_et: datetime | None = None,
    top_n: int = TOP_N,
) -> SelectionResult:
    """Score up to top_n candidates; pick highest composite (tie → better prep rank)."""
    sliced = list(candidates)[:top_n]
    scored: list[CandidateScore] = []
    for idx, c in enumerate(sliced):
        ticker = str(c.get("ticker") or "").upper()
        if not ticker:
            continue
        buy = c.get("limit_buy_price") or c.get("limit_buy") or c.get("recommended_entry")
        sell = c.get("limit_sell_price") or c.get("limit_sell") or c.get("target_price")
        stop = c.get("stop_price") or c.get("stop")
        shares = c.get("recommended_shares") or c.get("shares")
        if buy is None or sell is None or stop is None or shares is None:
            continue
        deploy = float(c.get("notional") or c.get("deploy") or c.get("suggested_size") or 0)
        rank = int(c.get("prep_rank") or c.get("rank") or (idx + 1))
        scored.append(
            score_candidate(
                rank=rank,
                ticker=ticker,
                limit_buy=float(buy),
                limit_sell=float(sell),
                stop=float(stop),
                shares=int(shares),
                deploy=deploy,
                bars_5m=bars_5m_by_ticker.get(ticker) or [],
                daily_bars=daily_by_ticker.get(ticker) or [],
                avg_range_pct=(
                    float(c["avg_range_pct"]) if c.get("avg_range_pct") is not None else None
                ),
                source=c.get("source"),
                as_of_et=as_of_et,
                raw=dict(c),
            )
        )

    if not scored:
        return SelectionResult(
            winner=None,
            scored=[],
            mode="best_tradable_top3",
            reason="No candidates with complete limit/stop/shares to score",
        )

    # Higher composite wins; tie → lower prep rank number (better).
    scored.sort(key=lambda s: (-s.composite, s.rank, s.ticker))
    winner = scored[0]
    others = ", ".join(f"{s.ticker}={s.composite:.3f}" for s in scored[1:])
    reason = (
        f"Selected {winner.ticker} (prep #{winner.rank}, score {winner.composite:.3f})"
        + (f"; also considered {others}" if others else "")
    )
    return SelectionResult(
        winner=winner,
        scored=scored,
        mode="best_tradable_top3",
        reason=reason,
    )
