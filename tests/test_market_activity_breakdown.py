"""Tests for Market Activity daily breakdown API helpers."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import init_db, insert_macro, insert_ohlcv_rows
from investment_agent.market_activity import (
    TRADE_MIN,
    build_daily_breakdown,
    list_daily_breakdowns,
    save_market_activity_evaluation,
)
from investment_agent.quote_snapshots import upsert_quote_snapshot


def _conn() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    path = Path(tmp.name)
    tmp.close()
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_spy_bars(conn: sqlite3.Connection, *, uptrend: bool = True) -> None:
    closes = [100 + i * (0.4 if uptrend else -0.15) for i in range(25)]
    rows = []
    end = datetime(2026, 8, 31, tzinfo=timezone.utc)
    for i, close in enumerate(closes):
        day = (end - timedelta(days=len(closes) - i)).strftime("%Y-%m-%d")
        rows.append(
            {
                "ticker": "SPY",
                "date": day,
                "open": close * 0.99,
                "high": close * 1.01,
                "low": close * 0.98,
                "close": close,
                "volume": 80_000_000,
                "source": "test",
            }
        )
    insert_ohlcv_rows(conn, rows)


def _seed_day_snapshot(conn: sqlite3.Connection, day: str, *, spy_change: float = -0.2) -> None:
    for sym, ch in [("SPY", spy_change), ("DIA", spy_change), ("QQQ", spy_change)]:
        base = 100.0
        price = base * (1 + ch / 100)
        upsert_quote_snapshot(
            conn,
            session_date_et=day,
            slot="plus_15m",
            ticker=sym,
            captured_at=f"{day}T14:00:00+00:00",
            price=price,
            open_px=base,
            prev_close=base * 0.99,
        )
    conn.commit()


def test_build_daily_breakdown_from_stored_evaluation() -> None:
    conn = _conn()
    try:
        day = "2026-08-28"
        _seed_spy_bars(conn)
        _seed_day_snapshot(conn, day, spy_change=-0.2)
        insert_macro(conn, "VIXCLS", day, 18.5, f"{day}T12:00:00+00:00")
        save_market_activity_evaluation(
            conn,
            session_date_et=day,
            captured_at=f"{day}T14:30:00+00:00",
            slot="plus_15m",
            score=54,
            band="below_average",
            allow_trade=False,
            bull_gate_ok=True,
            exit_alert=False,
            components={
                "market_direction": 46.0,
                "market_volume": 52.0,
                "volatility": 65.0,
                "momentum": 58.0,
                "sector_participation": 50.0,
                "news_catalysts": 70.0,
            },
            summary="test",
        )
        conn.commit()
        row = build_daily_breakdown(conn, day)
        assert row["score"] == 54
        assert row["allow_trade"] is False
        assert len(row["components"]) == 6
        assert row["components"][0]["key"] == "market_direction"
        assert any(g["key"] == "score" and not g["passed"] for g in row["gates"])
        assert row["trade_min"] == TRADE_MIN
    finally:
        conn.close()


def test_list_daily_breakdowns_returns_recent_days() -> None:
    conn = _conn()
    try:
        _seed_spy_bars(conn)
        for day, score in [("2026-08-27", 55), ("2026-08-28", 54)]:
            _seed_day_snapshot(conn, day)
            insert_macro(conn, "VIXCLS", day, 17.0, f"{day}T12:00:00+00:00")
            save_market_activity_evaluation(
                conn,
                session_date_et=day,
                captured_at=f"{day}T14:30:00+00:00",
                slot="plus_15m",
                score=score,
                band="below_average",
                allow_trade=False,
                bull_gate_ok=True,
                exit_alert=False,
                components={"market_direction": 45.0, "market_volume": 50.0},
                summary="test",
            )
        conn.commit()
        rows = list_daily_breakdowns(conn, days=5)
        assert len(rows) == 2
        assert rows[0]["session_date_et"] == "2026-08-28"
        assert rows[1]["session_date_et"] == "2026-08-27"
    finally:
        conn.close()


def test_daily_breakdown_api_route() -> None:
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from investment_agent.dashboard.app import app

    conn = _conn()
    try:
        day = "2026-08-29"
        _seed_spy_bars(conn)
        _seed_day_snapshot(conn, day)
        insert_macro(conn, "VIXCLS", day, 16.0, f"{day}T12:00:00+00:00")
        save_market_activity_evaluation(
            conn,
            session_date_et=day,
            captured_at=f"{day}T14:30:00+00:00",
            slot="plus_15m",
            score=56,
            band="below_average",
            allow_trade=False,
            bull_gate_ok=True,
            exit_alert=False,
            components={"market_direction": 48.0},
            summary="test",
        )
        conn.commit()
        db_path = Path(conn.execute("PRAGMA database_list").fetchone()[2])

        def fake_connect():
            c = sqlite3.connect(db_path)
            c.row_factory = sqlite3.Row
            return c

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                client = TestClient(app)
                resp = client.get("/api/market-activity/daily-breakdown?days=7")
                assert resp.status_code == 200
                data = resp.json()
                assert data["trade_min"] == TRADE_MIN
                assert len(data["days"]) >= 1
                assert data["days"][0]["components"]
    finally:
        conn.close()
