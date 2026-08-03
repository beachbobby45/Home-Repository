"""Daily and intraday OHLCV via yfinance (free fallback — Finnhub /stock/candle is paid-only)."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

REGIME_INDICES = ("SPY", "DIA", "QQQ")
ET = ZoneInfo("America/New_York")


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        out = df.copy()
        out.columns = out.columns.get_level_values(0)
        return out
    return df


def _safe_float(val) -> float:
    return float(val) if val is not None and not pd.isna(val) else 0.0


def get_daily_bars(symbol: str, lookback_days: int = 60) -> list[dict]:
    """Fetch daily OHLCV bars for a US ticker/ETF."""
    sym = symbol.upper()
    period = f"{max(lookback_days, 5)}d"
    df = yf.download(sym, period=period, progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise ValueError(f"No daily bars returned for {sym}")

    df = _flatten_columns(df)
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Unexpected yfinance columns for {sym}: {list(df.columns)}")

    rows: list[dict] = []
    for ts, row in df.iterrows():
        close = _safe_float(row["Close"])
        if close <= 0:
            continue
        date_str = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)[:10]
        volume = int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
        rows.append(
            {
                "ticker": sym,
                "date": date_str,
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": close,
                "volume": volume,
                "source": "yfinance",
            }
        )
    if not rows:
        raise ValueError(f"No valid daily bars for {sym}")
    return rows


def get_intraday_bars(
    symbol: str,
    *,
    lookback_days: int = 60,
    interval: str = "5m",
) -> list[dict]:
    """Fetch intraday OHLCV bars (default 5m — supports ~60d on Yahoo free tier)."""
    sym = symbol.upper()
    period = f"{max(lookback_days, 5)}d"
    df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise ValueError(f"No intraday bars returned for {sym}")

    df = _flatten_columns(df)
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Unexpected yfinance columns for {sym}: {list(df.columns)}")

    rows: list[dict] = []
    for ts, row in df.iterrows():
        close = _safe_float(row["Close"])
        if close <= 0:
            continue
        if hasattr(ts, "tz_convert"):
            ts_et = ts.tz_convert(ET)
        elif hasattr(ts, "tz_localize"):
            ts_et = ts.tz_localize(ET)
        else:
            ts_et = ts
        date_str = ts_et.strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": sym,
                "ts": ts_et.isoformat(),
                "date": date_str,
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": close,
                "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
                "source": "yfinance",
                "interval": interval,
            }
        )
    if not rows:
        raise ValueError(f"No valid intraday bars for {sym}")
    return rows


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
