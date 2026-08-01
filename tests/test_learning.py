"""Tests for learning report generation."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import seed_demo_db
from investment_agent.journal import get_completed_round_trips, get_open_positions
from investment_agent.learning import generate_learning_report, save_learning_report


def test_fifo_open_and_round_trips_on_demo():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "learn.db"
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        open_pos = get_open_positions(conn)
        trips = get_completed_round_trips(conn)
        assert len(open_pos) == 1
        assert open_pos[0]["ticker"] == "NVDA"
        assert len(trips) == 1
        assert trips[0]["ticker"] == "AAPL"
        assert trips[0]["same_day"] is True
        conn.close()


def test_learning_report_covers_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "learn.db"
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        report = generate_learning_report(conn)
        assert report["active_positions"]
        assert report["round_trips"]
        assert report["highlights"]
        assert report["claude_ready"] is False
        assert any("NVDA" in h or "round trip" in h.lower() for h in report["highlights"])
        rid = save_learning_report(conn, report)
        conn.commit()
        assert rid >= 1
        conn.close()
