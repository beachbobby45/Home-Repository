"""Tests for intraday trading day go/no-go panel."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_regime_snapshot, insert_ticker_metrics
from investment_agent.trading_day import (
    build_extended_session,
    build_trading_day_status,
    session_phase,
    stopped_out_today,
)

ET = ZoneInfo("America/New_York")


def _conn():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    return c, path


def _metric(conn, ticker: str):
    insert_ticker_metrics(
        conn,
        {
            "ticker": ticker,
            "computed_at": "2026-08-01T12:00:00+00:00",
            "adv_dollar": 50_000_000,
            "avg_range_pct": 3.0,
            "liquidity_cap": 400_000,
            "last_close": 100.0,
            "last_quote": 100.0,
            "meets_liquidity_min": True,
            "near_swing_target": True,
        },
    )


def test_session_phase_opening_wait():
    dt = datetime(2026, 8, 3, 9, 45, tzinfo=ET)
    assert session_phase(dt) == "opening_wait"


def test_session_phase_trade_window():
    dt = datetime(2026, 8, 3, 11, 0, tzinfo=ET)
    assert session_phase(dt) == "trade_window"


def test_trading_day_status_wait_during_opening():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": 0.2,
                "dia_change_pct": 0.1,
                "qqq_change_pct": 0.3,
                "all_indices_down": False,
                "block_new_longs": False,
                "summary": "Regime OK",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 9, 50, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "WAIT"
        assert status["session_phase"] == "opening_wait"
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_trading_day_no_go_when_regime_blocks():
    conn, path = _conn()
    try:
        insert_regime_snapshot(
            conn,
            {
                "captured_at": "2026-08-03T14:00:00+00:00",
                "spy_change_pct": -0.5,
                "dia_change_pct": -0.3,
                "qqq_change_pct": -0.1,
                "all_indices_down": True,
                "block_new_longs": True,
                "summary": "All down",
            },
        )
        conn.commit()
        from unittest.mock import patch

        with patch("investment_agent.trading_day.now_et", return_value=datetime(2026, 8, 3, 11, 0, tzinfo=ET)):
            status = build_trading_day_status(conn)
        assert status["verdict"] == "NO_GO"
        assert status["can_enter_new"] is False
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_weekend_headline_not_overwritten_by_tradability():
    """Weekend session message should stay in the regime banner even with skipped picks."""
    conn, path = _conn()
    try:
        from unittest.mock import patch

        skipped = [{"ticker": "TSCO"}, {"ticker": "FOXA"}]
        saturday = datetime(2026, 8, 15, 14, 0, tzinfo=ET)
        with patch("investment_agent.trading_day.now_et", return_value=saturday), patch(
            "investment_agent.trading_day.resolve_actionable_pick",
            return_value=(None, skipped),
        ):
            status = build_trading_day_status(conn)
        assert status["session_phase"] == "weekend"
        assert status["headline"] == "Market closed (weekend)"
        session_checks = [c for c in status["checks"] if c["name"] == "Session"]
        assert session_checks and "Weekend" in session_checks[0]["message"]
        top_checks = [c for c in status["checks"] if c["name"] == "Top pick"]
        assert top_checks and "TSCO" in top_checks[0]["message"]
    finally:
        conn.close()
        path.unlink(missing_ok=True)


def test_build_extended_session_none_during_rth():
    assert build_extended_session(
        phase="trade_window",
        quote={"price": 100.0},
        limit_buy=99.0,
        stop_price=98.0,
        limit_sell=101.0,
    ) is None


def test_build_extended_session_after_hours_flags():
    ext = build_extended_session(
        phase="after_hours",
        quote={
            "price": 162.0,
            "prev_close": 164.26,
            "captured_at": "2026-08-14T21:00:00+00:00",
        },
        limit_buy=163.17,
        stop_price=161.95,
        limit_sell=165.86,
        shares=61,
        rth_close=164.10,
    )
    assert ext is not None
    assert ext["label"] == "After hours"
    assert ext["price"] == 162.0
    assert ext["fill_status"]["default_assume_filled"] is False
    assert ext["fill_status"]["from_journal"] is False
    pos = ext["position"]
    assert pos["change_vs_entry_pct"] == round(((162.0 - 163.17) / 163.17) * 100, 3)
    flag_ids = {f["id"] for f in pos["flags"]}
    assert "below_limit_entry" in flag_ids
    assert "near_stop" in flag_ids
    assert pos["net_if_sold_now"] is not None
    assert pos["net_if_sold_now"] < 0


def test_build_extended_session_from_journal():
    ext = build_extended_session(
        phase="weekend",
        quote={"price": 162.0, "prev_close": 164.0},
        limit_buy=163.17,
        stop_price=161.95,
        limit_sell=165.86,
        shares=61,
        from_journal=True,
        journal_entry_price=163.25,
        journal_shares=60,
    )
    assert ext is not None
    assert ext["fill_status"]["from_journal"] is True
    assert ext["fill_status"]["default_assume_filled"] is True
    assert ext["fill_status"]["entry_price"] == 163.25
    assert ext["position"]["entry_label"] == "journal $163.25"


def test_build_extended_session_weekend_gap_flag():
    ext = build_extended_session(
        phase="weekend",
        quote={"price": 162.0, "prev_close": 164.0, "captured_at": "2026-08-15T15:00:00+00:00"},
        limit_buy=163.17,
        stop_price=161.95,
        limit_sell=165.86,
    )
    assert ext is not None
    assert ext["label"] == "Weekend (last quote)"
    flag_ids = {f["id"] for f in ext["position"]["flags"]}
    assert "weekend_gap_risk" in flag_ids


def test_build_extended_session_at_stop():
    ext = build_extended_session(
        phase="pre_market",
        quote={"price": 161.90, "prev_close": 164.0},
        limit_buy=163.17,
        stop_price=161.95,
        limit_sell=165.86,
    )
    assert ext is not None
    assert any(f["id"] == "at_or_below_stop" for f in ext["position"]["flags"])
