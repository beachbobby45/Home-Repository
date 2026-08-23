"""Tests for $5M scenario visualizer (Phase 6)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.scenario import build_scenario_visualizer, replay_actual_timeline


def test_replay_timeline_includes_start_and_months():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        timeline = replay_actual_timeline(conn)
        assert timeline[0].month_key == "start"
        assert timeline[0].tradable_balance == ORIGINAL_BASIS
        assert len(timeline) == expected["timeline_months"]
        month_keys = [p.month_key for p in timeline if p.month_key != "start"]
        assert "2026-06" in month_keys
        assert "2026-07" in month_keys
        assert expected["month_key"] in month_keys
        conn.close()


def test_june_realized_in_timeline_annual_sweep_at_year_end():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        timeline = replay_actual_timeline(conn)
        jun = next(p for p in timeline if p.month_key == "2026-06")
        assert abs(jun.monthly_realized_net - expected["jun_realized_net"]) < 0.02
        assert jun.sweep_total == 0.0
        aug = next(p for p in timeline if p.month_key == expected["month_key"])
        assert aug.sweep_total > 0
        conn.close()


def test_scenario_visualizer_structure():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sc.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        viz = build_scenario_visualizer(conn)
        assert viz["goal"] == 5_000_000
        assert len(viz["actual_timeline"]) >= 3
        assert "journal_pace" in viz["scenarios"]
        assert "required_10yr" in viz["scenarios"]
        assert "growth_plan_annual" in viz["scenarios"]
        assert "growth_plan_injection" in viz["scenarios"]
        assert viz["summary"]
        assert viz["scenarios"]["journal_pace"]["months_to_goal"] is not None
        assert viz["account_value"] > ORIGINAL_BASIS
        conn.close()


def test_empty_journal_still_returns_start_point():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "empty.db"
        from investment_agent.db import init_db

        init_db(path)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        viz = build_scenario_visualizer(conn)
        assert len(viz["actual_timeline"]) == 1
        assert viz["current_balance"] == ORIGINAL_BASIS
        conn.close()
