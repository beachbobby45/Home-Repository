"""Tests for yfinance daily bar provider."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.providers import yfinance_bars


def _sample_df() -> pd.DataFrame:
    idx = pd.to_datetime(["2026-07-29", "2026-07-30"])
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1_000_000, 1_100_000],
        },
        index=idx,
    )


@patch("investment_agent.providers.yfinance_bars.yf.download")
def test_get_daily_bars_parses_flat_columns(mock_download):
    mock_download.return_value = _sample_df()
    rows = yfinance_bars.get_daily_bars("SPY", lookback_days=30)
    assert len(rows) == 2
    assert rows[0]["ticker"] == "SPY"
    assert rows[0]["source"] == "yfinance"
    assert rows[-1]["close"] == 102.0


@patch("investment_agent.providers.yfinance_bars.yf.download")
def test_get_daily_bars_handles_multiindex_columns(mock_download):
    flat = _sample_df()
    flat.columns = pd.MultiIndex.from_product([flat.columns, ["SPY"]])
    mock_download.return_value = flat
    rows = yfinance_bars.get_daily_bars("SPY", lookback_days=30)
    assert rows[0]["open"] == 100.0
