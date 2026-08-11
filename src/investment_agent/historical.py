"""Historical OHLCV analysis — limited backfill, prior-day evaluation, period screening."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from typing import Any

from investment_agent.config import Settings
from investment_agent.db import (
    connect,
    get_active_watchlist,
    get_ohlcv_bars,
    get_ohlcv_coverage,
    init_db,
    insert_ohlcv_rows,
    log_ingest,
    upsert_watchlist,
)
from investment_agent.dollar_target import simulate_dollar_outcome
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.liquidity import DailyBar, compute_liquidity_metrics
from investment_agent.providers.yfinance_bars import get_daily_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS, STOP_PCT, TARGET_PCT

ET = ZoneInfo("America/New_York")
MIN_HISTORY_BARS = 5


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _prior_calendar_day(day: str) -> str:
    dt = datetime.strptime(day, "%Y-%m-%d")
    return (dt - timedelta(days=1)).strftime("%Y-%m-%d")


def open_based_range_pct(open_px: float, high: float, low: float) -> float:
    if open_px <= 0:
        return 0.0
    return ((high - low) / open_px) * 100.0


def _rows_to_daily_bars(rows: list[sqlite3.Row]) -> list[DailyBar]:
    return [
        DailyBar(
            high=float(r["high"]),
            low=float(r["low"]),
            close=float(r["close"]),
            volume=int(r["volume"]),
        )
        for r in rows
    ]


def simulate_intraday_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
) -> str:
    """Daily-bar approximation: target if high reached, else stop if low breached."""
    if open_px <= 0:
        return "invalid"
    target = open_px * (1 + target_pct / 100)
    stop = open_px * (1 - stop_pct / 100)
    if high >= target:
        return "target"
    if low <= stop:
        return "stop"
    return "neither"


def _latest_stored_trading_date(conn: sqlite3.Connection, before: str | None = None) -> str | None:
    clause = "WHERE date < ?" if before else ""
    params: tuple[Any, ...] = (before,) if before else ()
    row = conn.execute(
        f"SELECT MAX(date) AS d FROM ohlcv_daily {clause}",
        params,
    ).fetchone()
    return row["d"] if row and row["d"] else None


def evaluate_trading_day(
    conn: sqlite3.Connection,
    eval_date: str,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
) -> dict:
    """Compare predicted metrics (bars before eval_date) vs actual bar on eval_date."""
    tickers = [t for t in get_active_watchlist(conn) if t not in REGIME_ONLY_TICKERS]
    ticker_rows: list[dict] = []
    screened: list[dict] = []

    for ticker in tickers:
        bars = get_ohlcv_bars(conn, ticker, end_date=eval_date)
        if not bars:
            continue
        day_row = next((b for b in bars if b["date"] == eval_date), None)
        if day_row is None:
            continue
        history = [b for b in bars if b["date"] < eval_date]
        if len(history) < MIN_HISTORY_BARS:
            continue

        metrics = compute_liquidity_metrics(
            _rows_to_daily_bars(history),
            tradable_cash=tradable_cash,
        )
        open_px = float(day_row["open"])
        high = float(day_row["high"])
        low = float(day_row["low"])
        close = float(day_row["close"])
        actual_range = open_based_range_pct(open_px, high, low)
        would_screen = metrics.meets_liquidity_min and metrics.near_swing_target
        outcome = (
            simulate_intraday_outcome(open_px, high, low)
            if would_screen
            else None
        )
        dollar_outcome = (
            simulate_dollar_outcome(
                open_px,
                high,
                low,
                deploy_dollar=tradable_cash,
            )
            if would_screen
            else None
        )

        row = {
            "ticker": ticker,
            "eval_date": eval_date,
            "open": open_px,
            "high": high,
            "low": low,
            "close": close,
            "predicted_avg_range_pct": round(metrics.avg_range_pct, 2),
            "actual_range_pct": round(actual_range, 2),
            "range_delta_pct": round(actual_range - metrics.avg_range_pct, 2),
            "meets_liquidity": metrics.meets_liquidity_min,
            "near_swing_target": metrics.near_swing_target,
            "would_screen": would_screen,
            "simulated_outcome": outcome,
            "dollar_outcome": dollar_outcome,
            "liquidity_cap": round(metrics.liquidity_cap, 2),
        }
        ticker_rows.append(row)
        if would_screen:
            screened.append(row)

    targets = sum(1 for r in screened if r["simulated_outcome"] == "target")
    stops = sum(1 for r in screened if r["simulated_outcome"] == "stop")
    neither = sum(1 for r in screened if r["simulated_outcome"] == "neither")
    dollar_targets = sum(1 for r in screened if r["dollar_outcome"] == "target")
    dollar_stops = sum(1 for r in screened if r["dollar_outcome"] == "stop")
    dollar_neither = sum(1 for r in screened if r["dollar_outcome"] == "neither")

    return {
        "eval_date": eval_date,
        "tickers_evaluated": len(ticker_rows),
        "screened_matches": screened,
        "all_tickers": ticker_rows,
        "summary": {
            "screened_count": len(screened),
            "simulated_targets": targets,
            "simulated_stops": stops,
            "simulated_neither": neither,
            "dollar_targets": dollar_targets,
            "dollar_stops": dollar_stops,
            "dollar_neither": dollar_neither,
            "dollar_hit_rate_pct": round(
                100.0 * dollar_targets / max(dollar_targets + dollar_stops, 1),
                1,
            ),
            "avg_range_delta_pct": round(
                sum(r["range_delta_pct"] for r in ticker_rows) / len(ticker_rows),
                2,
            )
            if ticker_rows
            else None,
        },
    }


def evaluate_prior_day(
    conn: sqlite3.Connection,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
    reference_date: str | None = None,
) -> dict | None:
    """Evaluate the most recent complete trading day before reference_date (default: today ET)."""
    ref = reference_date or _today_et()
    eval_date = _latest_stored_trading_date(conn, before=ref)
    if not eval_date:
        eval_date = _prior_calendar_day(ref)
    if not eval_date:
        return None
    sample = conn.execute(
        "SELECT 1 FROM ohlcv_daily WHERE date = ? LIMIT 1",
        (eval_date,),
    ).fetchone()
    if not sample:
        return None
    result = evaluate_trading_day(conn, eval_date, tradable_cash=tradable_cash)
    result["reference_date"] = ref
    result["is_prior_day"] = eval_date == _prior_calendar_day(ref)
    return result


def build_historical_summary(conn: sqlite3.Connection) -> dict:
    coverage = get_ohlcv_coverage(conn)
    if not coverage:
        return {
            "has_data": False,
            "ticker_count": 0,
            "coverage": [],
            "earliest_date": None,
            "latest_date": None,
            "total_bars": 0,
        }
    earliest = min(c["first_date"] for c in coverage)
    latest = max(c["last_date"] for c in coverage)
    total = sum(c["bar_count"] for c in coverage)
    return {
        "has_data": True,
        "ticker_count": len(coverage),
        "coverage": coverage,
        "earliest_date": earliest,
        "latest_date": latest,
        "total_bars": total,
    }


def pull_historical_data(
    settings: Settings | None,
    *,
    tickers: list[str] | None = None,
    db_path=None,
    lookback_days: int = 60,
    use_active_watchlist: bool = True,
) -> dict:
    """Fetch limited daily OHLCV history into ohlcv_daily (yfinance, free tier)."""
    path = init_db(db_path)
    summary: dict = {
        "db_path": str(path),
        "lookback_days": lookback_days,
        "bars_inserted": 0,
        "errors": [],
        "tickers_processed": 0,
    }

    with sqlite3.connect(path) as raw:
        conn = raw
        conn.row_factory = sqlite3.Row

        if tickers is not None:
            symbols = [t.upper() for t in tickers]
            upsert_watchlist(conn, symbols)
        elif use_active_watchlist:
            symbols = get_active_watchlist(conn)
            if not symbols:
                from investment_agent.ingest import DEFAULT_TICKERS

                symbols = [t.upper() for t in DEFAULT_TICKERS]
                upsert_watchlist(conn, symbols)
        else:
            from investment_agent.ingest import DEFAULT_TICKERS

            symbols = [t.upper() for t in DEFAULT_TICKERS]
            upsert_watchlist(conn, symbols)

        summary["tickers"] = symbols

        for symbol in symbols:
            summary["tickers_processed"] += 1
            try:
                candles = get_daily_bars(symbol, lookback_days=lookback_days)
                count = insert_ohlcv_rows(conn, candles)
                summary["bars_inserted"] += count
                log_ingest(conn, "historical", "ok", f"{symbol}: {count} bars")
            except Exception as exc:
                log_ingest(conn, "historical", "error", f"{symbol}: {exc}")
                summary["errors"].append(f"{symbol}: {exc}")

        conn.commit()

    summary["error_count"] = len(summary["errors"])
    summary["ok"] = summary["error_count"] == 0
    with connect(path) as conn:
        summary["coverage"] = build_historical_summary(conn)
        from investment_agent.watchlist import compute_universe_stats

        summary["universe_stats"] = compute_universe_stats(conn)
    return summary


def evaluate_period(
    conn: sqlite3.Connection,
    start_date: str,
    end_date: str,
    *,
    tradable_cash: float = ORIGINAL_BASIS,
    trading_dates: list[str] | None = None,
) -> dict:
    """Evaluate each trading day in range that has OHLCV data."""
    if trading_dates is not None:
        dates = sorted(trading_dates)
    else:
        dates = [
            row["date"]
            for row in conn.execute(
                """
                SELECT DISTINCT date FROM ohlcv_daily
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC
                """,
                (start_date, end_date),
            ).fetchall()
        ]
    days: list[dict] = []
    total_dollar_targets = 0
    total_dollar_stops = 0
    for date in dates:
        day_eval = evaluate_trading_day(conn, date, tradable_cash=tradable_cash)
        total_dollar_targets += day_eval["summary"]["dollar_targets"]
        total_dollar_stops += day_eval["summary"]["dollar_stops"]
        days.append(
            {
                "date": date,
                "screened_count": day_eval["summary"]["screened_count"],
                "simulated_targets": day_eval["summary"]["simulated_targets"],
                "simulated_stops": day_eval["summary"]["simulated_stops"],
                "dollar_targets": day_eval["summary"]["dollar_targets"],
                "dollar_stops": day_eval["summary"]["dollar_stops"],
                "matches": [
                    {
                        "ticker": m["ticker"],
                        "outcome": m["simulated_outcome"],
                        "dollar_outcome": m.get("dollar_outcome"),
                        "actual_range_pct": m["actual_range_pct"],
                    }
                    for m in day_eval["screened_matches"]
                ],
            }
        )

    total_targets = sum(d["simulated_targets"] for d in days)
    total_stops = sum(d["simulated_stops"] for d in days)
    return {
        "start_date": start_date,
        "end_date": end_date,
        "days_evaluated": len(days),
        "days": days,
        "summary": {
            "total_screened_setups": sum(d["screened_count"] for d in days),
            "total_simulated_targets": total_targets,
            "total_simulated_stops": total_stops,
            "total_dollar_targets": total_dollar_targets,
            "total_dollar_stops": total_dollar_stops,
            "target_rate_pct": round(
                100.0 * total_targets / max(total_targets + total_stops, 1),
                1,
            ),
            "dollar_target_rate_pct": round(
                100.0 * total_dollar_targets / max(total_dollar_targets + total_dollar_stops, 1),
                1,
            ),
        },
    }
