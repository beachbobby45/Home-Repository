"""Tests for operator day log — attendance and NO TRADE tracking."""

from __future__ import annotations

import sqlite3

import pytest

from investment_agent.db import connect, init_db
from investment_agent.journal import insert_trade
from investment_agent.market_activity import save_market_activity_evaluation
from investment_agent.operator_day_log import (
    OUTCOME_NO_TRADE_OPERATOR,
    OUTCOME_NO_TRADE_SYSTEM,
    OUTCOME_PASS_NO_SETUP,
    OUTCOME_TRADED,
    SOURCE_AUTO_EOD,
    SOURCE_MANUAL,
    build_attendance_summary,
    get_operator_day,
    record_operator_day_from_eod,
    record_operator_day_from_journal,
    record_operator_day_manual,
    upsert_operator_day,
)


@pytest.fixture
def conn(tmp_path) -> sqlite3.Connection:
    path = init_db(tmp_path / "test.db")
    c = connect(path)
    yield c
    c.close()


def _seed_ohlcv_day(conn: sqlite3.Connection, day: str) -> None:
    conn.execute(
        """
        INSERT INTO ohlcv_daily (ticker, date, open, high, low, close, volume, source)
        VALUES ('SPY', ?, 100, 101, 99, 100.5, 1000000, 'test')
        """,
        (day,),
    )


def _seed_ma(conn: sqlite3.Connection, day: str, *, allow_trade: bool, score: int = 55) -> None:
    save_market_activity_evaluation(
        conn,
        session_date_et=day,
        captured_at="2026-09-03T14:00:00+00:00",
        slot="pre_open",
        score=score,
        band="average" if not allow_trade else "above_average",
        allow_trade=allow_trade,
        bull_gate_ok=True,
        exit_alert=False,
        components={},
        summary="test MA",
    )


def test_eod_auto_no_trade_system(conn: sqlite3.Connection) -> None:
    day = "2026-09-03"
    _seed_ohlcv_day(conn, day)
    _seed_ma(conn, day, allow_trade=False, score=58)
    result = record_operator_day_from_eod(conn, day)
    conn.commit()
    entry = result["entry"]
    assert entry["outcome"] == OUTCOME_NO_TRADE_SYSTEM
    assert entry["source"] == SOURCE_AUTO_EOD
    assert entry["allow_trade"] is False


def test_eod_auto_pass_no_setup(conn: sqlite3.Connection) -> None:
    day = "2026-09-04"
    _seed_ohlcv_day(conn, day)
    _seed_ma(conn, day, allow_trade=True, score=82)
    result = record_operator_day_from_eod(conn, day)
    conn.commit()
    assert result["entry"]["outcome"] == OUTCOME_PASS_NO_SETUP


def test_journal_auto_marks_traded(conn: sqlite3.Connection) -> None:
    day = "2026-09-05"
    _seed_ohlcv_day(conn, day)
    insert_trade(
        conn,
        ticker="AAPL",
        side="BUY",
        shares=10,
        price=100.0,
        executed_at="2026-09-05T14:30:00-07:00",
    )
    result = record_operator_day_from_journal(conn, day)
    conn.commit()
    assert result["entry"]["outcome"] == OUTCOME_TRADED
    assert result["entry"]["journal_trade_count"] == 1


def test_manual_not_overwritten_by_eod(conn: sqlite3.Connection) -> None:
    day = "2026-09-06"
    _seed_ohlcv_day(conn, day)
    _seed_ma(conn, day, allow_trade=True, score=80)
    record_operator_day_manual(
        conn,
        outcome=OUTCOME_NO_TRADE_OPERATOR,
        session_date_et=day,
        notes="Chose to wait",
    )
    conn.commit()
    record_operator_day_from_eod(conn, day)
    conn.commit()
    entry = get_operator_day(conn, day)
    assert entry is not None
    assert entry["outcome"] == OUTCOME_NO_TRADE_OPERATOR
    assert entry["source"] == SOURCE_MANUAL


def test_eod_upgrades_manual_when_journal_traded(conn: sqlite3.Connection) -> None:
    day = "2026-09-09"
    _seed_ohlcv_day(conn, day)
    record_operator_day_manual(
        conn,
        outcome=OUTCOME_PASS_NO_SETUP,
        session_date_et=day,
    )
    insert_trade(
        conn,
        ticker="MSFT",
        side="BUY",
        shares=5,
        price=200.0,
        executed_at="2026-09-09T10:00:00-07:00",
    )
    record_operator_day_from_eod(conn, day)
    conn.commit()
    entry = get_operator_day(conn, day)
    assert entry is not None
    assert entry["outcome"] == OUTCOME_TRADED


def test_no_trade_button_outcome(conn: sqlite3.Connection) -> None:
    day = "2026-09-10"
    _seed_ohlcv_day(conn, day)
    _seed_ma(conn, day, allow_trade=False)
    result = record_operator_day_manual(conn, outcome="NO_TRADE", session_date_et=day)
    conn.commit()
    assert result["entry"]["outcome"] == OUTCOME_NO_TRADE_SYSTEM

    day2 = "2026-09-11"
    _seed_ohlcv_day(conn, day2)
    _seed_ma(conn, day2, allow_trade=True, score=78)
    result2 = record_operator_day_manual(conn, outcome="NO_TRADE", session_date_et=day2)
    conn.commit()
    assert result2["entry"]["outcome"] == OUTCOME_NO_TRADE_OPERATOR


def test_attendance_summary(conn: sqlite3.Connection) -> None:
    for day in ("2026-09-01", "2026-09-02", "2026-09-03"):
        _seed_ohlcv_day(conn, day)
    upsert_operator_day(
        conn,
        session_date_et="2026-09-01",
        outcome=OUTCOME_NO_TRADE_SYSTEM,
        source=SOURCE_AUTO_EOD,
        force=True,
    )
    conn.commit()
    summary = build_attendance_summary(conn, since="2026-09-01")
    assert summary["trading_days"] == 3
    assert summary["attended_days"] == 1
    assert summary["missing_days"] == 2
    assert "2026-09-02" in summary["missing_dates"]
