"""Empty Yahoo 5m feed must not finalize the paper day before the fill deadline."""

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
from investment_agent.execution.paper_ledger import (
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_session_log,
    upsert_session_log,
)
from investment_agent.execution.paper_runner import (
    _is_retryable_empty_bars,
    _session_already_final,
    run_paper_tick,
)
from investment_agent.execution.paper_sim import simulate_round_trip_5m
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE

ET = ZoneInfo("America/New_York")


class EmptyBarsSimTests(unittest.TestCase):
    def test_empty_bars_before_deadline_waits(self) -> None:
        sim = simulate_round_trip_5m(
            [],
            buy=100.0,
            sell=101.5,
            stop=99.0,
            shares=10,
            buy_fee=0.0,
            sell_fee=0.0,
            as_of_et=datetime(2026, 10, 30, 10, 0, tzinfo=ET),
        )
        self.assertEqual(sim["scenario"], "waiting_for_bars")
        self.assertFalse(sim["complete"])
        self.assertFalse(sim["filled"])

    def test_empty_bars_after_deadline_finalizes(self) -> None:
        after = datetime(2026, 10, 30, 12, 45, tzinfo=ET)
        self.assertGreater(after.timetz().replace(tzinfo=None), LIMIT_FILL_DEADLINE)
        sim = simulate_round_trip_5m(
            [],
            buy=100.0,
            sell=101.5,
            stop=99.0,
            shares=10,
            buy_fee=0.0,
            sell_fee=0.0,
            as_of_et=after,
        )
        self.assertEqual(sim["scenario"], "no_5m_bars")
        self.assertTrue(sim["complete"])

    def test_empty_bars_force_path_as_of_none_finalizes(self) -> None:
        sim = simulate_round_trip_5m(
            [],
            buy=100.0,
            sell=101.5,
            stop=99.0,
            shares=10,
            buy_fee=0.0,
            sell_fee=0.0,
            as_of_et=None,
        )
        self.assertEqual(sim["scenario"], "no_5m_bars")
        self.assertTrue(sim["complete"])


class EmptyBarsRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        ensure_paper_accounts(self.conn, starting_cash=5_000.0)
        self.day = "2026-10-30"
        self.signal = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "FDS",
            "limit_buy": 300.0,
            "limit_sell": 310.0,
            "stop": 297.0,
            "shares": 16,
            "deploy": 4800.0,
            "allow_trade": True,
            "ma_score": 51,
            "day_gate_mode": "produce",
        }

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def _tick(self, when: datetime, *, bars: list | None = None):
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(paper_runner, "datetime") as dt_mod,
            patch.object(paper_runner, "_plan_signal", return_value=self.signal),
            patch.object(paper_runner, "_fetch_day_bars", return_value=bars if bars is not None else []),
        ):
            dt_mod.now.return_value = when
            return run_paper_tick(self.conn, session_date_et=self.day)

    def test_overnight_empty_bars_stays_in_progress(self) -> None:
        out = self._tick(datetime(2026, 10, 30, 3, 23, tzinfo=ET), bars=[])
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "in_progress")
        self.assertEqual(gate["scenario"], "waiting_for_bars")
        self.assertFalse(bool(gate["filled"]))

    def test_premature_no_5m_complete_reopens_when_bars_arrive(self) -> None:
        # Simulate the Oct bug: early complete with no_5m_bars.
        upsert_session_log(
            self.conn,
            {
                "session_date_et": self.day,
                "account_name": ACCOUNT_GATE,
                "ticker": "FDS",
                "allow_trade": True,
                "ma_score": 51,
                "day_gate_mode": "produce",
                "status": "complete",
                "scenario": "no_5m_bars",
                "filled": False,
                "net_pnl": 0.0,
                "detail": "No 5m bars for this ticker/date",
            },
        )
        self.conn.commit()
        existing = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        self.assertTrue(_is_retryable_empty_bars(existing))
        self.assertFalse(
            _session_already_final(
                existing,
                signal_ok=True,
                as_of_et=datetime(2026, 10, 30, 10, 0, tzinfo=ET),
                force_complete=False,
            )
        )

        bars = [
            {
                "ts": f"{self.day}T09:35:00-04:00",
                "open": 301.0,
                "high": 302.0,
                "low": 299.0,  # trade through 300
                "close": 300.5,
            },
            {
                "ts": f"{self.day}T10:05:00-04:00",
                "open": 300.5,
                "high": 311.0,
                "low": 300.0,
                "close": 310.5,
            },
        ]
        out = self._tick(datetime(2026, 10, 30, 10, 10, tzinfo=ET), bars=bars)
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertTrue(bool(gate["filled"]))
        self.assertEqual(gate["status"], "complete")
        self.assertNotEqual(gate["scenario"], "no_5m_bars")

    def test_after_deadline_empty_bars_finalizes(self) -> None:
        out = self._tick(datetime(2026, 10, 30, 12, 45, tzinfo=ET), bars=[])
        self.assertTrue(out["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "complete")
        self.assertEqual(gate["scenario"], "no_5m_bars")


if __name__ == "__main__":
    unittest.main()
