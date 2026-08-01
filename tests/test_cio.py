"""Tests for CIO summary (Phase 5)."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.cio import build_cio_summary
from investment_agent.demo_seed import expected_demo_summary, seed_demo_db


def test_cio_summary_on_demo_data():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cio.db"
        seed_demo_db(path)
        expected = expected_demo_summary()
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cio = build_cio_summary(conn)
        assert cio["headline"]
        assert cio["narrative"]
        assert cio["action_items"]
        assert "research" in cio["sub_agents"]
        assert "learning" in cio["sub_agents"]
        assert cio["tradable_cash"] == expected["tradable_cash"] or abs(
            cio["tradable_cash"] - expected["tradable_cash"]
        ) < 0.02
        assert cio["claude_ready"] is False
        assert cio["block_new_longs"] is False
        conn.close()
