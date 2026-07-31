"""Phase 1 ingestion orchestration — FRED + Finnhub quotes + yfinance bars, no Claude."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from investment_agent.config import Settings
from investment_agent.db import (
    init_db,
    insert_macro,
    insert_ohlcv_rows,
    insert_quote,
    insert_regime_snapshot,
    insert_ticker_metrics,
    log_ingest,
    upsert_watchlist,
)
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.fred import fetch_vix, utc_now_iso as fred_now
from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now
from investment_agent.providers.yfinance_bars import get_daily_bars
from investment_agent.regime import (
    REGIME_SYMBOLS,
    evaluate_regime,
    index_quote_from_finnhub,
)

# Regime indices + starter watchlist (expand in Phase 2 screener)
DEFAULT_TICKERS = [
    "SPY",
    "DIA",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "META",
    "TSLA",
    "IWM",
]

MACRO_SERIES = ["VIXCLS"]


def run_ingest(
    settings: Settings,
    tickers: list[str] | None = None,
    db_path: Path | None = None,
    lookback_days: int = 60,
    tradable_cash: float = ORIGINAL_BASIS,
) -> dict:
    """Fetch macro + quotes + daily bars; compute liquidity/range metrics + regime."""
    path = init_db(db_path)
    symbols = [t.upper() for t in (tickers or DEFAULT_TICKERS)]
    summary: dict = {"db_path": str(path), "tickers": symbols, "errors": []}
    index_quotes: dict = {}

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row
        upsert_watchlist(conn, symbols)

        # --- FRED macro ---
        try:
            captured = fred_now()
            obs_date, vix = fetch_vix(settings.fred_api_key)
            insert_macro(conn, "VIXCLS", obs_date, vix, captured)
            log_ingest(conn, "fred", "ok", f"VIXCLS={vix} on {obs_date}")
            summary["vix"] = vix
        except Exception as exc:
            log_ingest(conn, "fred", "error", str(exc))
            summary["errors"].append(f"fred: {exc}")

        # --- Finnhub live quotes ---
        fh = FinnhubClient(settings.finnhub_api_key)
        try:
            for symbol in symbols:
                try:
                    q = fh.get_quote(symbol)
                    insert_quote(
                        conn,
                        {
                            "ticker": symbol,
                            "captured_at": fh_now(),
                            "price": float(q["c"]),
                            "open": float(q.get("o") or 0) or None,
                            "high": float(q.get("h") or 0) or None,
                            "low": float(q.get("l") or 0) or None,
                            "prev_close": float(q.get("pc") or 0) or None,
                        },
                    )
                    if symbol in REGIME_SYMBOLS:
                        index_quotes[symbol] = index_quote_from_finnhub(symbol, q)
                    log_ingest(conn, "finnhub", "ok", f"quote {symbol}")
                except Exception as exc:
                    log_ingest(conn, "finnhub", "error", f"quote {symbol}: {exc}")
                    summary["errors"].append(f"quote {symbol}: {exc}")
        finally:
            fh.close()

        # --- yfinance daily bars (Finnhub /stock/candle requires paid tier) ---
        for symbol in symbols:
            try:
                candles = get_daily_bars(symbol, lookback_days=lookback_days)
                insert_ohlcv_rows(conn, candles)

                bars = [
                    DailyBar(
                        high=r["high"],
                        low=r["low"],
                        close=r["close"],
                        volume=r["volume"],
                    )
                    for r in sorted(candles, key=lambda x: x["date"])
                ]
                metrics = compute_liquidity_metrics(
                    bars, tradable_cash=tradable_cash
                )
                last_close = bars[-1].close if bars else 0.0
                last_quote_row = conn.execute(
                    """
                    SELECT price FROM quotes
                    WHERE ticker = ?
                    ORDER BY captured_at DESC
                    LIMIT 1
                    """,
                    (symbol,),
                ).fetchone()
                last_quote = (
                    float(last_quote_row["price"]) if last_quote_row else last_close
                )
                insert_ticker_metrics(
                    conn,
                    {
                        "ticker": symbol,
                        "computed_at": datetime.now(timezone.utc)
                        .replace(microsecond=0)
                        .isoformat(),
                        "adv_dollar": metrics.adv_dollar,
                        "avg_range_pct": metrics.avg_range_pct,
                        "liquidity_cap": metrics.liquidity_cap,
                        "last_close": last_close,
                        "last_quote": last_quote,
                        "meets_liquidity_min": metrics.meets_liquidity_min,
                        "near_swing_target": metrics.near_swing_target,
                    },
                )
                log_ingest(conn, "yfinance", "ok", symbol)
            except Exception as exc:
                log_ingest(conn, "yfinance", "error", f"{symbol}: {exc}")
                summary["errors"].append(f"bars {symbol}: {exc}")

        # --- Regime gate (requires SPY/DIA/QQQ quotes) ---
        if all(sym in index_quotes for sym in REGIME_SYMBOLS):
            try:
                regime = evaluate_regime(index_quotes, fh_now())
                insert_regime_snapshot(
                    conn,
                    {
                        "captured_at": regime.captured_at,
                        "spy_change_pct": regime.spy_change_pct,
                        "dia_change_pct": regime.dia_change_pct,
                        "qqq_change_pct": regime.qqq_change_pct,
                        "all_indices_down": regime.all_indices_down,
                        "block_new_longs": regime.block_new_longs,
                        "summary": regime.summary,
                    },
                )
                log_ingest(conn, "regime", "ok", regime.summary)
                summary["regime"] = {
                    "block_new_longs": regime.block_new_longs,
                    "summary": regime.summary,
                    "spy_change_pct": regime.spy_change_pct,
                    "dia_change_pct": regime.dia_change_pct,
                    "qqq_change_pct": regime.qqq_change_pct,
                }
            except Exception as exc:
                log_ingest(conn, "regime", "error", str(exc))
                summary["errors"].append(f"regime: {exc}")
        else:
            missing = [s for s in REGIME_SYMBOLS if s not in index_quotes]
            summary["errors"].append(
                f"regime: missing index quotes for {', '.join(missing)}"
            )

        conn.commit()

    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    return summary
