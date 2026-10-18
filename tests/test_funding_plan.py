"""Funding plan + paper phase capital bounds."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient

from investment_agent.capital_builder import (
    PAPER_PHASE_START,
    PAPER_PHASE_TARGET,
    build_capital_builder_progress,
)
from investment_agent.dashboard.app import app
from investment_agent.db import init_db
from investment_agent.execution.ops_audit import set_ledger_source
from investment_agent.execution.paper_ledger import ensure_paper_accounts
from investment_agent.funding_plan import build_funding_plan_payload, funding_plan_rows


class FundingPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        import sqlite3

        self.conn = sqlite3.connect(self.db)
        self.conn.row_factory = sqlite3.Row
        ensure_paper_accounts(self.conn, starting_cash=5_000)
        set_ledger_source(self.conn, "paper")
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_stages_include_rh_and_deposits(self) -> None:
        rows = funding_plan_rows()
        ids = [r["id"] for r in rows]
        self.assertIn("paper_start", ids)
        self.assertIn("rh_live_1", ids)
        self.assertIn("deposit_2", ids)
        self.assertIn("deposit_4", ids)
        rh = next(r for r in rows if r["id"] == "rh_live_1")
        self.assertEqual(rh["cash_in"], 5_000)
        self.assertEqual(rh["date"], "2026-12-01")

    def test_payload_and_capital_builder_use_5k_band(self) -> None:
        fp = build_funding_plan_payload(self.conn)
        self.assertEqual(fp["paper_starting_cash"], 5_000)
        self.assertEqual(fp["phase_start"], 5_000)
        self.assertEqual(fp["phase_target"], 20_000)
        cb = build_capital_builder_progress(self.conn)
        self.assertEqual(cb.phase1_start, PAPER_PHASE_START)
        self.assertEqual(cb.phase1_target, PAPER_PHASE_TARGET)
        self.assertEqual(cb.current_equity, 5_000.0)

    def test_api_funding_plan(self) -> None:
        import sqlite3

        def fake_connect():
            c = sqlite3.connect(self.db)
            c.row_factory = sqlite3.Row
            return c

        with patch("investment_agent.dashboard.app.connect", fake_connect):
            with patch("investment_agent.dashboard.app.init_db", lambda: self.db):
                http = TestClient(app)
                r = http.get("/api/funding-plan")
                self.assertEqual(r.status_code, 200, r.text)
                body = r.json()
                self.assertEqual(body["paper_equity"], 5_000)
                self.assertGreaterEqual(len(body["stages"]), 5)


if __name__ == "__main__":
    unittest.main()
