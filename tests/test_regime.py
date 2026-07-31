"""Tests for regime gate logic."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.regime import (
    IndexQuote,
    evaluate_regime,
    index_quote_from_finnhub,
    intraday_change_pct,
)


def test_intraday_change_vs_open():
    assert abs(intraday_change_pct(101.0, open_price=100.0) - 1.0) < 0.001


def test_intraday_change_falls_back_to_prev_close():
    assert abs(intraday_change_pct(99.0, prev_close=100.0) - (-1.0)) < 0.001


def test_all_indices_down_blocks_new_longs():
    quotes = {
        "SPY": IndexQuote("SPY", 100, 101, 100, -0.99),
        "DIA": IndexQuote("DIA", 100, 101, 100, -0.50),
        "QQQ": IndexQuote("QQQ", 100, 101, 100, -0.10),
    }
    snap = evaluate_regime(quotes, "2026-07-31T12:00:00+00:00")
    assert snap.all_indices_down is True
    assert snap.block_new_longs is True


def test_mixed_indices_allows_longs():
    quotes = {
        "SPY": IndexQuote("SPY", 101, 100, 100, 1.0),
        "DIA": IndexQuote("DIA", 99, 100, 100, -1.0),
        "QQQ": IndexQuote("QQQ", 99, 100, 100, -1.0),
    }
    snap = evaluate_regime(quotes, "2026-07-31T12:00:00+00:00")
    assert snap.block_new_longs is False


def test_index_quote_from_finnhub():
    q = index_quote_from_finnhub("SPY", {"c": 100.0, "o": 99.0, "pc": 98.0})
    assert q.symbol == "SPY"
    assert abs(q.intraday_change_pct - ((100 - 99) / 99 * 100)) < 0.01
