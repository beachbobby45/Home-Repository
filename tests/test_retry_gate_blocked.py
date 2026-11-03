"""Early day-gate NO must mean 'not yet' until 12:30 ET, not 'day over'."""

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
    ACCOUNT_ALL,
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_paper_balance,
    get_session_log,
)
from investment_agent.execution.paper_runner import (
    _is_retryable_gate_blocked,
    _session_already_final,
    run_paper_tick,
)
from investment_agent.pullback_entry import LIMIT_FILL_DEADLINE

ET = ZoneInfo("America/New_York")
DAY = "2026-11-03"


def _bars_fill_then_target(day: str) -> list[dict]:
    # Fill bar trades through buy 99.5 without touching stop 98.5; next bar hits target 101.
    return [
        {
            "ts": f"{day}T09:35:00-05:00",
            "open": 100.0,
            "high": 100.5,
            "low": 99.0,
            "close": 99.8,
        },
        {
            "ts": f"{day}T10:05:00-05:00",
            "open": 100.0,
            "high": 101.5,
            "low": 100.0,
            "close": 101.2,
        },
    ]


class RetryGateBlockedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        ensure_paper_accounts(self.conn, starting_cash=5_000.0)
        self.day = DAY

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def _tick(
        self,
        when: datetime,
        *,
        gate_signal: dict,
        bars: list | None = None,
    ):
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(paper_runner, "datetime") as dt_mod,
            patch.object(paper_runner, "_plan_signal", return_value=gate_signal),
            patch.object(
                paper_runner,
                "_fetch_day_bars",
                return_value=bars if bars is not None else _bars_fill_then_target(self.day),
            ),
        ):
            dt_mod.now.return_value = when
            return run_paper_tick(self.conn, session_date_et=self.day)

    def test_helpers_recognize_gate_blocked(self) -> None:
        existing = {
            "status": "skipped_gate",
            "scenario": "gate_blocked",
            "filled": 0,
            "detail": "allow_trade=false — gate_approved book skips",
        }
        self.assertTrue(_is_retryable_gate_blocked(existing))
        self.assertFalse(
            _session_already_final(
                existing,
                signal_ok=True,
                as_of_et=datetime(2026, 11, 3, 10, 0, tzinfo=ET),
                force_complete=False,
            )
        )
        after = datetime(2026, 11, 3, 12, 45, tzinfo=ET)
        self.assertGreater(after.timetz().replace(tzinfo=None), LIMIT_FILL_DEADLINE)
        self.assertTrue(
            _session_already_final(
                existing,
                signal_ok=True,
                as_of_et=after,
                force_complete=False,
            )
        )

    def test_early_gate_no_then_later_yes_can_fill(self) -> None:
        """Reproduces Nov 3 hole: MA 40 skip at open, later allow_trade arms GPN."""
        blocked = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "LH",
            "limit_buy": 99.5,
            "limit_sell": 101.0,
            "stop": 98.5,
            "shares": 50,
            "deploy": 5000.0,
            "allow_trade": False,
            "ma_score": 40,
            "day_gate_mode": "produce",
        }
        opened = {
            **blocked,
            "ticker": "GPN",
            "allow_trade": True,
            "ma_score": 55,
        }

        out1 = self._tick(datetime(2026, 11, 3, 9, 32, tzinfo=ET), gate_signal=blocked)
        self.assertTrue(out1["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "skipped_gate")
        self.assertEqual(gate["scenario"], "gate_blocked")
        self.assertEqual(gate["ticker"], "LH")
        self.assertFalse(bool(gate["filled"]))

        out2 = self._tick(
            datetime(2026, 11, 3, 11, 0, tzinfo=ET),
            gate_signal=opened,
            bars=_bars_fill_then_target(self.day),
        )
        self.assertTrue(out2["ok"])
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertTrue(bool(gate["filled"]), msg=f"expected fill after gate open, got {gate}")
        self.assertEqual(gate["status"], "complete")
        self.assertEqual(gate["ticker"], "GPN")
        self.assertNotEqual(gate["scenario"], "gate_blocked")
        self.assertIn("target", str(gate.get("scenario") or ""))
        bal = get_paper_balance(self.conn, ACCOUNT_GATE)
        self.assertGreater(float(bal["equity"]), 5000.0)

    def test_still_blocked_refreshes_ma_before_deadline(self) -> None:
        first = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "LH",
            "limit_buy": 99.5,
            "limit_sell": 101.0,
            "stop": 98.5,
            "shares": 50,
            "deploy": 5000.0,
            "allow_trade": False,
            "ma_score": 40,
            "day_gate_mode": "produce",
        }
        later = {**first, "ticker": "GPN", "ma_score": 48}
        self._tick(datetime(2026, 11, 3, 9, 32, tzinfo=ET), gate_signal=first)
        self._tick(datetime(2026, 11, 3, 10, 15, tzinfo=ET), gate_signal=later)
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "skipped_gate")
        self.assertEqual(gate["ma_score"], 48)
        self.assertEqual(gate["ticker"], "GPN")
        self.assertFalse(bool(gate["filled"]))

    def test_after_deadline_gate_blocked_stays_final(self) -> None:
        blocked = {
            "ok": True,
            "session_date_et": self.day,
            "ticker": "LH",
            "limit_buy": 99.5,
            "limit_sell": 101.0,
            "stop": 98.5,
            "shares": 50,
            "deploy": 5000.0,
            "allow_trade": False,
            "ma_score": 40,
            "day_gate_mode": "produce",
        }
        opened = {
            **blocked,
            "ticker": "GPN",
            "allow_trade": True,
            "ma_score": 60,
        }
        self._tick(datetime(2026, 11, 3, 9, 32, tzinfo=ET), gate_signal=blocked)
        self._tick(
            datetime(2026, 11, 3, 12, 45, tzinfo=ET),
            gate_signal=opened,
            bars=_bars_fill_then_target(self.day),
        )
        gate = get_session_log(self.conn, self.day, ACCOUNT_GATE)
        assert gate is not None
        self.assertEqual(gate["status"], "skipped_gate")
        self.assertEqual(gate["ticker"], "LH")
        self.assertFalse(bool(gate["filled"]))
        # Shadow may still have traded; gate must not.
        _ = get_session_log(self.conn, self.day, ACCOUNT_ALL)


if __name__ == "__main__":
    unittest.main()
