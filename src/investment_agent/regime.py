"""Regime gate — triple-index intraday down blocks new longs (Product Spec v3)."""

from __future__ import annotations

from dataclasses import dataclass

REGIME_SYMBOLS = ("SPY", "DIA", "QQQ")


@dataclass(frozen=True)
class IndexQuote:
    symbol: str
    price: float
    open: float | None
    prev_close: float | None
    intraday_change_pct: float


@dataclass(frozen=True)
class RegimeSnapshot:
    captured_at: str
    spy_change_pct: float
    dia_change_pct: float
    qqq_change_pct: float
    all_indices_down: bool
    block_new_longs: bool
    summary: str


def intraday_change_pct(
    price: float,
    open_price: float | None = None,
    prev_close: float | None = None,
) -> float:
    """Percent change vs session open; fall back to prior close if open missing."""
    if open_price and open_price > 0:
        return ((price - open_price) / open_price) * 100.0
    if prev_close and prev_close > 0:
        return ((price - prev_close) / prev_close) * 100.0
    return 0.0


def index_quote_from_finnhub(symbol: str, quote: dict) -> IndexQuote:
    price = float(quote["c"])
    open_px = float(quote["o"]) if quote.get("o") else None
    prev = float(quote["pc"]) if quote.get("pc") else None
    change = intraday_change_pct(price, open_px, prev)
    return IndexQuote(
        symbol=symbol.upper(),
        price=price,
        open=open_px,
        prev_close=prev,
        intraday_change_pct=change,
    )


def evaluate_regime(
    index_quotes: dict[str, IndexQuote],
    captured_at: str,
) -> RegimeSnapshot:
    """True when SPY, DIA, and QQQ are all down intraday."""
    changes: dict[str, float] = {}
    for sym in REGIME_SYMBOLS:
        q = index_quotes.get(sym)
        if q is None:
            raise ValueError(f"Missing regime quote for {sym}")
        changes[sym] = q.intraday_change_pct

    all_down = all(changes[sym] < 0 for sym in REGIME_SYMBOLS)
    block = all_down
    if block:
        summary = (
            "Regime: SPY, DIA, QQQ all down intraday — "
            "no new longs until indices recover."
        )
    else:
        parts = ", ".join(f"{s} {changes[s]:+.2f}%" for s in REGIME_SYMBOLS)
        summary = f"Regime OK — {parts}"

    return RegimeSnapshot(
        captured_at=captured_at,
        spy_change_pct=changes["SPY"],
        dia_change_pct=changes["DIA"],
        qqq_change_pct=changes["QQQ"],
        all_indices_down=all_down,
        block_new_longs=block,
        summary=summary,
    )
