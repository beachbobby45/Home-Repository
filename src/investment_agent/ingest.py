"""Phase 1 ingestion orchestration — FRED + Finnhub quotes + yfinance bars, no Claude."""

from __future__ import annotations

import gc
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from investment_agent.config import Settings
from investment_agent.db import (
    connect,
    get_active_watchlist,
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
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_FULL_INGEST,
    record_screen_action,
)

# Commit + GC every N symbols during large watchlist ingests (S&P 500 ~537 tickers).
_BARS_BATCH_SIZE = 25

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


def _parse_iso_age_hours(iso_ts: str | None) -> float | None:
    if not iso_ts:
        return None
    try:
        ts = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 3600.0
    except ValueError:
        return None


def _needs_quote_refresh(
    conn: sqlite3.Connection,
    symbol: str,
    *,
    stale_hours: float,
    force_symbols: set[str] | None = None,
) -> bool:
    if force_symbols and symbol in force_symbols:
        return True
    row = conn.execute(
        """
        SELECT captured_at FROM quotes
        WHERE ticker = ?
        ORDER BY captured_at DESC
        LIMIT 1
        """,
        (symbol,),
    ).fetchone()
    age = _parse_iso_age_hours(row["captured_at"] if row else None)
    return age is None or age >= stale_hours


def _needs_bars_refresh(
    conn: sqlite3.Connection,
    symbol: str,
    *,
    stale_hours: float,
    force_symbols: set[str] | None = None,
) -> bool:
    if force_symbols and symbol in force_symbols:
        return True
    metrics = conn.execute(
        """
        SELECT computed_at FROM ticker_metrics
        WHERE ticker = ?
        ORDER BY computed_at DESC
        LIMIT 1
        """,
        (symbol,),
    ).fetchone()
    age = _parse_iso_age_hours(metrics["computed_at"] if metrics else None)
    return age is None or age >= stale_hours


def run_ingest(
    settings: Settings,
    tickers: list[str] | None = None,
    db_path: Path | None = None,
    lookback_days: int = 60,
    tradable_cash: float = ORIGINAL_BASIS,
    incremental: bool = False,
    stale_hours: float = 20.0,
    quote_stale_hours: float | None = None,
    bar_stale_hours: float | None = None,
) -> dict:
    """Fetch macro + quotes + daily bars; compute liquidity/range metrics + regime."""
    from investment_agent.db_maintenance import acquire_ingest_lock, release_ingest_lock

    try:
        acquire_ingest_lock(detail="run_ingest")
    except RuntimeError as exc:
        return {
            "ok": False,
            "partial": False,
            "errors": [str(exc)],
            "quotes_refreshed": 0,
            "quotes_skipped": 0,
            "bars_refreshed": 0,
            "bars_skipped": 0,
            "error_count": 1,
        }
    try:
        return _run_ingest_body(
            settings,
            tickers=tickers,
            db_path=db_path,
            lookback_days=lookback_days,
            tradable_cash=tradable_cash,
            incremental=incremental,
            stale_hours=stale_hours,
            quote_stale_hours=quote_stale_hours,
            bar_stale_hours=bar_stale_hours,
        )
    finally:
        release_ingest_lock()


def _run_ingest_body(
    settings: Settings,
    tickers: list[str] | None = None,
    db_path: Path | None = None,
    lookback_days: int = 60,
    tradable_cash: float = ORIGINAL_BASIS,
    incremental: bool = False,
    stale_hours: float = 20.0,
    quote_stale_hours: float | None = None,
    bar_stale_hours: float | None = None,
) -> dict:
    """Internal ingest implementation."""
    q_stale = stale_hours if quote_stale_hours is None else quote_stale_hours
    b_stale = stale_hours if bar_stale_hours is None else bar_stale_hours
    path = init_db(db_path)
    if tickers is not None:
        symbols = [t.upper() for t in tickers]
    else:
        with connect(path) as conn:
            symbols = get_active_watchlist(conn)
        if not symbols:
            symbols = [t.upper() for t in DEFAULT_TICKERS]
    summary: dict = {
        "db_path": str(path),
        "tickers": symbols,
        "errors": [],
        "incremental": incremental,
        "stale_hours": stale_hours,
        "quote_stale_hours": q_stale,
        "bar_stale_hours": b_stale,
        "quotes_refreshed": 0,
        "quotes_skipped": 0,
        "bars_refreshed": 0,
        "bars_skipped": 0,
    }
    index_quotes: dict = {}
    force = set(REGIME_SYMBOLS)

    with connect(path) as conn:
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
                if incremental and not _needs_quote_refresh(
                    conn, symbol, stale_hours=q_stale, force_symbols=force
                ):
                    summary["quotes_skipped"] += 1
                    if symbol in REGIME_SYMBOLS:
                        row = conn.execute(
                            """
                            SELECT price, open, prev_close FROM quotes
                            WHERE ticker = ?
                            ORDER BY captured_at DESC
                            LIMIT 1
                            """,
                            (symbol,),
                        ).fetchone()
                        if row:
                            index_quotes[symbol] = index_quote_from_finnhub(
                                symbol,
                                {
                                    "c": row["price"],
                                    "o": row["open"] or row["price"],
                                    "pc": row["prev_close"] or row["price"],
                                },
                            )
                    continue
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
                    summary["quotes_refreshed"] += 1
                    if symbol in REGIME_SYMBOLS:
                        index_quotes[symbol] = index_quote_from_finnhub(symbol, q)
                    log_ingest(conn, "finnhub", "ok", f"quote {symbol}")
                except Exception as exc:
                    log_ingest(conn, "finnhub", "error", f"quote {symbol}: {exc}")
                    summary["errors"].append(f"quote {symbol}: {exc}")
        finally:
            fh.close()

        # --- yfinance daily bars (Finnhub /stock/candle requires paid tier) ---
        bars_pending_commit = 0
        total_symbols = len(symbols)
        for idx, symbol in enumerate(symbols, start=1):
            if incremental and not _needs_bars_refresh(
                conn, symbol, stale_hours=b_stale, force_symbols=force
            ):
                summary["bars_skipped"] += 1
                continue
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
                summary["bars_refreshed"] += 1
                bars_pending_commit += 1
                if bars_pending_commit >= _BARS_BATCH_SIZE:
                    conn.commit()
                    bars_pending_commit = 0
                    gc.collect()
                if idx % 50 == 0 or idx == total_symbols:
                    print(
                        f"  bars progress: {idx}/{total_symbols} "
                        f"({summary['bars_refreshed']} refreshed, "
                        f"{summary['bars_skipped']} skipped, "
                        f"{len(summary['errors'])} errors)",
                        flush=True,
                    )
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

        # --- Company news (top 50 ranked + open positions) ---
        try:
            from investment_agent.news_service import ingest_news_for_targets

            news_summary = ingest_news_for_targets(conn, settings)
            summary["news"] = news_summary
            if news_summary.get("inserted"):
                log_ingest(
                    conn,
                    "finnhub_news",
                    "ok",
                    f"inserted {news_summary['inserted']} headlines for "
                    f"{len(news_summary.get('tickers') or [])} tickers",
                )
            if news_summary.get("errors"):
                for err in news_summary["errors"]:
                    summary["errors"].append(f"news: {err}")
        except Exception as exc:
            log_ingest(conn, "finnhub_news", "error", str(exc))
            summary["errors"].append(f"news: {exc}")

        conn.commit()

        action_id = ACTION_DAILY_INGEST if incremental else ACTION_FULL_INGEST
        record_screen_action(
            conn,
            action_id,
            detail=(
                f"{summary['quotes_refreshed']} quotes, {summary['bars_refreshed']} bars refreshed"
            ),
        )
        conn.commit()

    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    summary["partial"] = (
        not summary["ok"]
        and (summary["bars_refreshed"] > 0 or summary["quotes_refreshed"] > 0)
    )
    return summary
