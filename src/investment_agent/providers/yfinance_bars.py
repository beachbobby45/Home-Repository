"""Daily and intraday OHLCV via yfinance (free fallback — Finnhub /stock/candle is paid-only)."""

from __future__ import annotations

import gc
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

REGIME_INDICES = ("SPY", "DIA", "QQQ")
ET = ZoneInfo("America/New_York")

_MIN_INTERVAL_SEC = float(os.environ.get("YFINANCE_MIN_INTERVAL_SEC", "0.15"))
_MAX_RETRIES = int(os.environ.get("YFINANCE_MAX_RETRIES", "3"))
_RETRY_BASE_SEC = float(os.environ.get("YFINANCE_RETRY_BASE_SEC", "1.0"))
_last_fetch_at = 0.0
_cache_configured = False


def _configure_yfinance_cache() -> None:
    global _cache_configured
    if _cache_configured:
        return
    cache_dir = os.environ.get("YFINANCE_CACHE_DIR")
    if cache_dir:
        path = Path(cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        try:
            yf.set_tz_cache_location(str(path))
        except Exception:
            pass
    _cache_configured = True


def _throttle() -> None:
    global _last_fetch_at
    now = time.monotonic()
    wait = _MIN_INTERVAL_SEC - (now - _last_fetch_at)
    if wait > 0:
        time.sleep(wait)
    _last_fetch_at = time.monotonic()


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        out = df.copy()
        out.columns = out.columns.get_level_values(0)
        return out
    return df


def _safe_float(val) -> float:
    return float(val) if val is not None and not pd.isna(val) else 0.0


def _fetch_history(
    sym: str,
    *,
    period: str,
    interval: str | None = None,
) -> pd.DataFrame:
    """Fetch OHLCV with retries; one Ticker at a time to limit open FDs."""
    _configure_yfinance_cache()
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        ticker = None
        try:
            _throttle()
            ticker = yf.Ticker(sym)
            if interval:
                df = ticker.history(
                    period=period, interval=interval, auto_adjust=False
                )
            else:
                df = ticker.history(period=period, auto_adjust=False)
            if df is None or df.empty:
                raise ValueError(f"No bars returned for {sym}")
            return _flatten_columns(df)
        except Exception as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BASE_SEC * (2**attempt))
        finally:
            if ticker is not None:
                del ticker
            gc.collect()
    assert last_exc is not None
    raise last_exc


def _rows_from_daily_df(df: pd.DataFrame, sym: str) -> list[dict]:
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


def get_daily_bars(symbol: str, lookback_days: int = 60) -> list[dict]:
    """Fetch daily OHLCV bars for a US ticker/ETF."""
    sym = symbol.upper()
    period = f"{max(lookback_days, 5)}d"
    df = _fetch_history(sym, period=period)
    return _rows_from_daily_df(df, sym)


def get_intraday_bars(
    symbol: str,
    *,
    lookback_days: int = 60,
    interval: str = "5m",
) -> list[dict]:
    """Fetch intraday OHLCV bars (default 5m — supports ~60d on Yahoo free tier)."""
    sym = symbol.upper()
    # Yahoo free tier: 1m limited to ~7 calendar days per request
    if interval == "1m":
        period = f"{min(max(lookback_days, 1), 7)}d"
    else:
        period = f"{max(lookback_days, 5)}d"
    df = _fetch_history(sym, period=period, interval=interval)

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
