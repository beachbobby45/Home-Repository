"""Tests for demo seed data."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import build_dashboard_summary
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db
from investment_agent.monitor import run_monitor_cycle


def test_seed_demo_db_populates_all_sections():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo.db"
        seed_demo_db(path)
        expected = expected_demo_summary()

        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row

        assert conn.execute("SELECT COUNT(*) FROM queue_items").fetchone()[0] == expected["queue_count"]
        assert conn.execute("SELECT COUNT(*) FROM trade_journal").fetchone()[0] == expected["journal_count"]
        assert conn.execute("SELECT value FROM macro_snapshots WHERE series_id='VIXCLS'").fetchone()[0] == expected["vix"]

        summary = build_dashboard_summary(conn)
        assert abs(summary.tradable_cash - expected["tradable_cash"]) < 0.02
        assert abs(summary.monthly_realized_net - expected["monthly_realized_net"]) < 0.02
        assert summary.block_new_longs is False

        mon = run_monitor_cycle(conn)
        assert mon["new_alerts"] >= 1

        conn.close()


def test_seed_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo.db"
        seed_demo_db(path)
        seed_demo_db(path)
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM queue_items").fetchone()[0]
        conn.close()
        assert count == expected_demo_summary()["queue_count"]
