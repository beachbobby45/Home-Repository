"""Tests for screen action timestamps."""

from __future__ import annotations

from investment_agent.db import connect, init_db
from investment_agent.screen_actions import (
    ACTION_DAILY_INGEST,
    ACTION_SP500,
    get_screen_action_status,
    record_screen_action,
)


def test_record_and_fetch_screen_action(tmp_path):
    path = init_db(tmp_path / "t.db")
    conn = connect(path)
    try:
        record_screen_action(conn, ACTION_SP500, detail="503 tickers")
        conn.commit()
        status = get_screen_action_status(conn)
        assert status[ACTION_SP500]["completed_at"]
        assert status[ACTION_SP500]["detail"] == "503 tickers"
        assert status[ACTION_SP500]["source"] == "recorded"
        assert status[ACTION_DAILY_INGEST]["completed_at"] is None or status[ACTION_DAILY_INGEST]["source"] == "none"
    finally:
        conn.close()
