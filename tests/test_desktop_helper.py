"""Tests for desktop status formatting and rhythm timestamps."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.daily_rhythm import get_daily_rhythm_status
from investment_agent.db import init_db
from investment_agent.desktop_status import format_last_run
from investment_agent.screen_actions import ACTION_REFRESH_LIVE, record_screen_action


def test_format_last_run_none():
    assert format_last_run(None) == "Last run: not yet"


def test_format_last_run_iso():
    iso = "2026-08-17T15:30:00+00:00"
    text = format_last_run(iso)
    assert "Last run:" in text
    assert "PT" in text


def test_daily_rhythm_includes_refresh_live_last_at():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "t.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        record_screen_action(conn, ACTION_REFRESH_LIVE, detail="test")
        conn.commit()
        status = get_daily_rhythm_status(conn)
        conn.close()
        step3 = next(s for s in status["steps"] if s["id"] == "before_buy")
        assert step3["last_at"] is not None
