"""Tests for daily rhythm status and trading candidates."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from investment_agent.daily_rhythm import get_daily_rhythm_status, ingest_schedule_installed
from investment_agent.db import init_db


def test_get_daily_rhythm_status_has_three_steps():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "rhythm.db"
        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        status = get_daily_rhythm_status(conn)
        conn.close()
        assert len(status["steps"]) == 3
        assert status["steps"][0]["id"] == "after_close"
        assert status["steps"][1]["id"] == "pre_market"
        assert status["steps"][2]["id"] == "before_buy"
        assert isinstance(status["schedule_installed"], bool)


def test_ingest_schedule_installed_is_bool():
    assert isinstance(ingest_schedule_installed(), bool)
