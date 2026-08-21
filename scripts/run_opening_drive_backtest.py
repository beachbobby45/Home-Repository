#!/usr/bin/env python3
"""Opening Drive backtest — replay scoring on stored daily OHLCV.

Uses a documented 9:40 ET price proxy when 5m bars are unavailable:
  price_940 = open + (high - open) * 0.55
  low_940   = low (conservative — full session low)

Pass `--intraday` to fetch 5m bars via yfinance (slower, more accurate).
Results are written to data/backtests/opening_drive_<timestamp>.json by default.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.opening_drive import (
    OPENING_DRIVE_PASS_MIN,
    evaluate_opening_drive,
    opening_drive_window_active,
)

ET = ZoneInfo("America/New_York")
PROXY_EARLY_SESSION_RATIO = 0.55


def _trading_dates(conn: sqlite3.Connection, *, start: str, end: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE ticker = 'SPY' AND date >= ? AND date <= ?
        ORDER BY date
        """,
        (start, end),
    ).fetchall()
    return [row["date"] for row in rows]


def _bar(conn: sqlite3.Connection, ticker: str, day: str) -> dict | None:
    row = conn.execute(
        """
        SELECT open, high, low, close, volume
        FROM ohlcv_daily
        WHERE ticker = ? AND date = ?
        """,
        (ticker.upper(), day),
    ).fetchone()
    if not row:
        return None
    return {
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": int(row["volume"]),
    }


def _prev_close(conn: sqlite3.Connection, ticker: str, day: str) -> float | None:
    row = conn.execute(
        """
        SELECT close FROM ohlcv_daily
        WHERE ticker = ? AND date < ?
        ORDER BY date DESC LIMIT 1
        """,
        (ticker.upper(), day),
    ).fetchone()
    return float(row["close"]) if row else None


def _proxy_quote(bar: dict, prev_close: float | None) -> dict:
    open_px = bar["open"]
    high = bar["high"]
    low = bar["low"]
    price = open_px + (high - open_px) * PROXY_EARLY_SESSION_RATIO
    return {
        "price": round(price, 4),
        "open": open_px,
        "high": high,
        "low": low,
        "prev_close": prev_close,
    }


def _price_at_940_5m(ticker: str, day: str) -> dict | None:
    """Fetch 5m bar near 9:40 ET; return quote dict or None."""
    try:
        import yfinance as yf
    except ImportError:
        return None

    sym = ticker.upper()
    start = day
    end = (datetime.strptime(day, "%Y-%m-%d").date()).strftime("%Y-%m-%d")
    df = yf.Ticker(sym).history(start=start, end=end, interval="5m", auto_adjust=False)
    if df is None or df.empty:
        return None
    target = datetime.strptime(day, "%Y-%m-%d").replace(
        hour=9, minute=40, tzinfo=ET
    )
    # Pick bar at or just after 9:40 ET
    idx = df.index
    if idx.tz is None:
        idx = idx.tz_localize("UTC").tz_convert(ET)
    else:
        idx = idx.tz_convert(ET)
    df = df.copy()
    df.index = idx
    day_rows = df[df.index.date == target.date()]
    if day_rows.empty:
        return None
    after = day_rows[day_rows.index >= target]
    row = after.iloc[0] if not after.empty else day_rows.iloc[-1]
    open_px = float(day_rows.iloc[0]["Open"])
    return {
        "price": float(row["Close"]),
        "open": open_px,
        "high": float(day_rows["High"].max()),
        "low": float(day_rows["Low"].min()),
        "prev_close": None,
    }


def run_backtest(
    conn: sqlite3.Connection,
    *,
    tickers: list[str],
    start_date: str,
    end_date: str,
    deploy_dollar: float,
    net_target: float,
    use_intraday: bool,
    market_activity_score: int = 72,
) -> dict:
    market_activity = {
        "allow_trade": True,
        "band": "above_average" if market_activity_score >= 70 else "average",
        "score": market_activity_score,
    }
    days = _trading_dates(conn, start=start_date, end=end_date)
    results: list[dict] = []
    pass_count = 0
    watch_count = 0
    fade_count = 0

    for day in days:
        when = datetime.strptime(day, "%Y-%m-%d").replace(hour=9, minute=40, tzinfo=ET)
        if not opening_drive_window_active(when):
            continue
        spy_bar = _bar(conn, "SPY", day)
        if not spy_bar:
            continue
        spy_prev = _prev_close(conn, "SPY", day)
        spy_quote = _proxy_quote(spy_bar, spy_prev)
        if use_intraday:
            intraday_spy = _price_at_940_5m("SPY", day)
            if intraday_spy:
                intraday_spy["prev_close"] = spy_prev
                spy_quote = intraday_spy

        for ticker in tickers:
            bar = _bar(conn, ticker, day)
            if not bar:
                continue
            prev = _prev_close(conn, ticker, day)
            quote = _proxy_quote(bar, prev)
            if use_intraday:
                intraday = _price_at_940_5m(ticker, day)
                if intraday:
                    intraday["prev_close"] = prev
                    quote = intraday

            eval_result = evaluate_opening_drive(
                conn,
                ticker,
                quote=quote,
                spy_quote=spy_quote,
                market_activity=market_activity,
                deploy_dollar=deploy_dollar,
                net_target=net_target,
                when=when,
            )
            row = {
                "date": day,
                "ticker": ticker.upper(),
                "score": eval_result["score"],
                "verdict": eval_result["verdict"],
                "eligible_early_entry": eval_result["eligible_early_entry"],
                "gap_at_open_pct": eval_result.get("gap_at_open_pct"),
                "change_vs_open_pct": eval_result.get("change_vs_open_pct"),
                "rs_vs_spy_pct": eval_result.get("rs_vs_spy_pct"),
                "price_proxy": quote["price"],
                "open": quote["open"],
            }
            results.append(row)
            if eval_result["verdict"] == "pass":
                pass_count += 1
            elif eval_result["verdict"] == "watch":
                watch_count += 1
            elif eval_result["verdict"] == "fade":
                fade_count += 1

    total = len(results)
    return {
        "generated_at": datetime.now(ET).replace(microsecond=0).isoformat(),
        "start_date": start_date,
        "end_date": end_date,
        "tickers": [t.upper() for t in tickers],
        "method": "5m_intraday" if use_intraday else f"daily_proxy_ratio_{PROXY_EARLY_SESSION_RATIO}",
        "pass_min": OPENING_DRIVE_PASS_MIN,
        "market_activity_assumed": market_activity,
        "summary": {
            "evaluations": total,
            "pass": pass_count,
            "watch": watch_count,
            "fade": fade_count,
            "pass_rate_pct": round(100.0 * pass_count / total, 2) if total else 0.0,
        },
        "days": len(days),
        "results": results,
    }


def _default_tickers(conn: sqlite3.Connection, limit: int = 10) -> list[str]:
    rows = conn.execute(
        """
        SELECT ticker FROM watchlist
        WHERE active = 1
        ORDER BY ticker
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    if rows:
        return [row["ticker"] for row in rows]
    return ["AAPL", "MSFT", "NVDA", "META", "GOOGL"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Opening Drive backtest on stored OHLCV")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--start", default="2026-01-02", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="End date YYYY-MM-DD (default: today ET)")
    parser.add_argument("--tickers", nargs="*", default=None, help="Tickers to test")
    parser.add_argument("--top", type=int, default=10, help="Watchlist tickers if --tickers omitted")
    parser.add_argument("--capital", type=float, default=10_000.0)
    parser.add_argument("--net-target", type=float, default=150.0)
    parser.add_argument("--ma-score", type=int, default=72, help="Assumed market activity score")
    parser.add_argument("--intraday", action="store_true", help="Use yfinance 5m bars (slow)")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path (default: data/backtests/opening_drive_<ts>.json)",
    )
    args = parser.parse_args()

    end = args.end or datetime.now(ET).strftime("%Y-%m-%d")
    path = init_db(args.db)
    conn = connect(path)
    conn.row_factory = sqlite3.Row
    try:
        tickers = args.tickers or _default_tickers(conn, limit=args.top)
        payload = run_backtest(
            conn,
            tickers=tickers,
            start_date=args.start,
            end_date=end,
            deploy_dollar=args.capital,
            net_target=args.net_target,
            use_intraday=args.intraday,
            market_activity_score=args.ma_score,
        )
    finally:
        conn.close()

    out = args.output
    if out is None:
        ts = datetime.now(ET).strftime("%Y%m%d_%H%M%S")
        out = ROOT / "data" / "backtests" / f"opening_drive_{ts}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))

    s = payload["summary"]
    print("=== OPENING DRIVE BACKTEST ===")
    print(f"Period:     {payload['start_date']} → {payload['end_date']} ({payload['days']} SPY sessions)")
    print(f"Method:     {payload['method']}")
    print(f"Tickers:    {', '.join(payload['tickers'])}")
    print(f"Evaluations:{s['evaluations']} ticker-days")
    print(f"PASS:       {s['pass']} ({s['pass_rate_pct']}%)")
    print(f"WATCH:      {s['watch']}")
    print(f"FADE:       {s['fade']}")
    print(f"Report:     {out}")


if __name__ == "__main__":
    main()
