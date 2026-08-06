"""Tests for intraday tradability assessment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.tradability import assess_entry_tradability


def _assess(entry: float, quote: dict, **kwargs):
    return assess_entry_tradability(
        quote=quote,
        entry_price=entry,
        deploy_dollar=ORIGINAL_BASIS,
        net_target=150.0,
        **kwargs,
    )


def test_nflx_mon_aug3_open_entry_not_tradable():
    """Mon 8/3 — high $73.95 missed ~$73.97 target from open."""
    quote = {
        "price": 72.77,
        "open": 72.77,
        "high": 73.95,
        "low": 72.18,
        "prev_close": 72.39,
    }
    result = _assess(72.77, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert result["max_net_at_day_high"] is not None
    assert result["max_net_at_day_high"] < 150.0


def test_nflx_wed_aug5_gap_up_not_tradable():
    """Wed 8/5 — gap up ~2.1%, little upside from open."""
    quote = {
        "price": 75.11,
        "open": 75.11,
        "high": 75.30,
        "low": 73.16,
        "prev_close": 73.57,
    }
    result = _assess(75.11, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("Gap up" in b for b in result["blockers"])


def test_nflx_tue_aug4_missed_window_if_target_already_touched():
    """Tue 8/4 — if high already hit target but price retraced, not tradable NOW."""
    quote = {
        "price": 72.51,
        "open": 72.51,
        "high": 73.75,
        "low": 72.30,
        "prev_close": 73.33,
    }
    result = _assess(72.51, quote, avg_range_pct=3.0)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("missed window" in b.lower() for b in result["blockers"])


def test_room_to_target_early_session_caution():
    """Early session — high hasn't developed enough yet; marginal, not blocked."""
    quote = {
        "price": 50.0,
        "open": 50.0,
        "high": 50.25,
        "low": 49.85,
        "prev_close": 49.8,
    }
    result = _assess(50.0, quote, avg_range_pct=3.0)
    assert result["verdict"] in ("CAUTION", "TRADABLE")


def test_chase_above_open_blocks_entry():
    quote = {
        "price": 101.0,
        "open": 100.0,
        "high": 102.0,
        "low": 99.5,
        "prev_close": 99.0,
    }
    result = _assess(101.0, quote)
    assert result["verdict"] == "NOT_TRADABLE"
    assert any("above open" in b.lower() for b in result["blockers"])


def test_target_already_hit_and_retraced():
    quote = {
        "price": 99.5,
        "open": 98.0,
        "high": 101.5,
        "low": 97.5,
        "prev_close": 97.0,
    }
    result = _assess(100.0, quote)
    assert result["verdict"] in ("NOT_TRADABLE", "CAUTION")
