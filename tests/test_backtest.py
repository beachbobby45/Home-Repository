"""Tests for intraday backtest engine."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.backtest import (
    _bar_exit_price,
    _regime_blocks,
    _simulate_trading_day,
)


def test_bar_exit_target():
    px, reason = _bar_exit_price(target=101.13, stop=99.5, bar={"open": 100, "high": 102, "low": 99.8})
    assert reason == "target"
    assert px == 101.13


def test_bar_exit_stop_when_both_hit():
    px, reason = _bar_exit_price(target=101.13, stop=99.5, bar={"open": 100, "high": 102, "low": 99})
    assert reason == "stop"
    assert px == 99.5


def test_regime_blocks_when_all_indices_down():
    index_bars = {
        "SPY": [{"open": 100, "close": 99, "high": 100, "low": 98}],
        "DIA": [{"open": 100, "close": 99, "high": 100, "low": 98}],
        "QQQ": [{"open": 100, "close": 99, "high": 100, "low": 98}],
    }
    assert _regime_blocks(index_bars, 0) is True


def test_simulate_day_single_target_trade():
    spy = [
        {"ts": "2026-07-01T09:30:00-04:00", "open": 100, "high": 100, "low": 100, "close": 100},
        {"ts": "2026-07-01T09:35:00-04:00", "open": 100, "high": 102, "low": 99.9, "close": 101.5},
    ]
    aapl = [
        {"ts": "2026-07-01T09:30:00-04:00", "open": 100, "high": 100.5, "low": 99.9, "close": 100},
        {"ts": "2026-07-01T09:35:00-04:00", "open": 100, "high": 102, "low": 99.9, "close": 101.5},
    ]
    index_bars = {"SPY": spy, "DIA": spy, "QQQ": spy}
    trades, cash = _simulate_trading_day(
        date="2026-07-01",
        ordered_tickers=["AAPL"],
        rank_by_ticker={"AAPL": 0.9},
        liquidity_caps={"AAPL": 10_000},
        ticker_bars={"AAPL": aapl},
        index_bars=index_bars,
        cash=10_000,
        buy_fee=7,
        sell_fee=7,
    )
    assert len(trades) == 1
    assert trades[0].exit_reason == "target"
    assert cash > 10_000
