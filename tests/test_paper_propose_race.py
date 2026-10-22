"""Paper worker must not lock the day on early propose failures."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import (
    ACCOUNT_ALL,
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_session_log,
    upsert_session_log,
)
from investment_agent.execution import paper_runner
from investment_agent.execution.paper_runner import run_paper_tick

ET = ZoneInfo("America/New_York")


class PaperProposeRaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        ensure_paper_accounts(self.conn, starting_cash=5_000.0)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_early_propose_failure_is_waiting_not_final(self) -> None:
        morning = datetime(2026, 10, 22, 8, 0, tzinfo=ET)
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(
                paper_runner,
                "_plan_signal",
                return_value={
                    "ok": False,
                    "error": "No top pick available to propose",
                    "session_date_et": "2026-10-22",
                },
            ),
            patch.object(paper_runner, "datetime") as dt_mod,
        ):
            dt_mod.now.return_value = morning
            out = run_paper_tick(self.conn, session_date_et="2026-10-22")
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, "2026-10-22", ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "waiting_signal")
        self.assertEqual(gate["scenario"], "propose_failed")

    def test_retry_after_prep_unlocks_no_signal_propose_failed(self) -> None:
        for name in (ACCOUNT_GATE, ACCOUNT_ALL):
            upsert_session_log(
                self.conn,
                {
                    "session_date_et": "2026-10-22",
                    "account_name": name,
                    "status": "no_signal",
                    "scenario": "propose_failed",
                    "filled": False,
                    "net_pnl": 0.0,
                    "detail": "No top pick available to propose",
                    "settled_cash_before": 5000.0,
                    "settled_cash_after": 5000.0,
                    "equity_after": 5000.0,
                },
            )
        signal = {
            "ok": True,
            "session_date_et": "2026-10-22",
            "ticker": "ACN",
            "limit_buy": 226.92,
            "limit_sell": 230.97,
            "stop": 225.22,
            "shares": 22,
            "deploy": 5000.0,
            "allow_trade": False,
            "ma_score": 43,
            "day_gate_mode": "produce",
        }
        morning = datetime(2026, 10, 22, 10, 0, tzinfo=ET)
        bars = [
            {
                "ts": "2026-10-22T10:00:00-04:00",
                "open": 228.0,
                "high": 229.0,
                "low": 226.0,
                "close": 227.0,
            }
        ]
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(paper_runner, "_plan_signal", return_value=signal),
            patch.object(paper_runner, "_fetch_day_bars", return_value=bars),
            patch.object(paper_runner, "datetime") as dt_mod,
        ):
            dt_mod.now.return_value = morning
            out = run_paper_tick(self.conn, session_date_et="2026-10-22")
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, "2026-10-22", ACCOUNT_GATE)
        all_arm = get_session_log(self.conn, "2026-10-22", ACCOUNT_ALL)
        assert gate is not None and all_arm is not None
        self.assertEqual(gate["status"], "skipped_gate")
        self.assertEqual(gate["ticker"], "ACN")
        self.assertIn(all_arm["status"], {"in_progress", "complete"})
        self.assertEqual(all_arm["ticker"], "ACN")


if __name__ == "__main__":
    unittest.main()
