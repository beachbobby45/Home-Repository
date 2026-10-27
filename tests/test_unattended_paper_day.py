"""Full autonomous paper-day timeline: midnight wait → prep → arm → fill/exit."""

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
from investment_agent.execution import paper_runner
from investment_agent.execution.ops_audit import paper_day_audit_exists
from investment_agent.execution.paper_ledger import (
    ACCOUNT_ALL,
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_paper_balance,
    get_session_log,
)
from investment_agent.execution.paper_runner import run_paper_tick

ET = ZoneInfo("America/New_York")


def _bars_fill_then_target(day: str = "2026-10-23") -> list[dict]:
    return [
        {
            "ts": f"{day}T09:35:00-04:00",
            "open": 100.0,
            "high": 100.5,
            "low": 99.0,
            "close": 99.8,
        },
        {
            "ts": f"{day}T10:05:00-04:00",
            "open": 100.0,
            "high": 101.5,
            "low": 100.0,
            "close": 101.2,
        },
    ]


class UnattendedPaperDayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        ensure_paper_accounts(self.conn, starting_cash=5_000.0)
        self.day = "2026-10-23"

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def _tick(
        self,
        when: datetime,
        *,
        signal: dict | None = None,
        bars: list | None = None,
    ):
        no_signal = {
            "ok": False,
            "error": "No top pick available to propose",
            "session_date_et": self.day,
        }
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(paper_runner, "datetime") as dt_mod,
            patch.object(paper_runner, "_plan_signal", return_value=signal or no_signal),
            patch.object(paper_runner, "_fetch_day_bars", return_value=bars or []),
        ):
            dt_mod.now.return_value = when
            return run_paper_tick(self.conn, session_date_et=self.day)

    def test_midnight_to_fill_go_day(self) -> None:
        out1 = self._tick(datetime(2026, 10, 23, 0, 5, tzinfo=ET))
        self.assertTrue(out1["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "waiting_signal")

        signal = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "TEST",
            "limit_buy": 99.5,
            "limit_sell": 101.0,
            "stop": 98.5,
            "shares": 50,
            "deploy": 5000.0,
            "allow_trade": True,
            "ma_score": 62,
            "day_gate_mode": "produce",
        }
        out2 = self._tick(
            datetime(2026, 10, 23, 10, 30, tzinfo=ET),
            signal=signal,
            bars=_bars_fill_then_target(self.day),
        )
        self.assertTrue(out2["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        all_arm = get_session_log(self.conn, self.day, ACCOUNT_ALL)
        assert gate is not None and all_arm is not None
        self.assertEqual(gate["status"], "complete")
        self.assertTrue(gate["filled"])
        self.assertEqual(gate["ticker"], "TEST")
        self.assertEqual(all_arm["status"], "complete")
        self.assertTrue(all_arm["filled"])
        self.assertTrue(paper_day_audit_exists(self.conn, self.day))
        bal = get_paper_balance(self.conn, ACCOUNT_GATE)
        self.assertNotEqual(float(bal["equity"]), 5000.0)

    def test_no_go_gate_skips_but_all_signals_can_fill(self) -> None:
        self._tick(datetime(2026, 10, 23, 0, 5, tzinfo=ET))
        signal = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "TEST",
            "limit_buy": 99.5,
            "limit_sell": 101.0,
            "stop": 98.5,
            "shares": 50,
            "deploy": 5000.0,
            "allow_trade": False,
            "ma_score": 40,
            "day_gate_mode": "produce",
        }
        self._tick(
            datetime(2026, 10, 23, 10, 0, tzinfo=ET),
            signal=signal,
            bars=_bars_fill_then_target(self.day),
        )
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        all_arm = get_session_log(self.conn, self.day, ACCOUNT_ALL)
        assert gate is not None and all_arm is not None
        self.assertEqual(gate["status"], "skipped_gate")
        self.assertFalse(bool(gate["filled"]))
        self.assertIn(all_arm["status"], {"complete", "in_progress"})
        self.assertEqual(all_arm["ticker"], "TEST")

    def test_after_deadline_without_pick_finalizes_no_signal(self) -> None:
        self._tick(datetime(2026, 10, 23, 0, 5, tzinfo=ET))
        # v1 fill deadline is 12:30 ET — 12:00 still waits; 12:45 finalizes.
        still_waiting = self._tick(datetime(2026, 10, 23, 12, 0, tzinfo=ET))
        self.assertTrue(still_waiting["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "waiting_signal")

        out = self._tick(datetime(2026, 10, 23, 12, 45, tzinfo=ET))
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "no_signal")


if __name__ == "__main__":
    unittest.main()
