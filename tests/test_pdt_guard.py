"""Day-trade weekly ops guard (post–PDT regime)."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from investment_agent.db import connect, init_db
from investment_agent.execution.pdt_guard import (
    can_open_day_trade,
    count_day_trades_in_week,
    max_day_trades_per_week,
    record_day_trade,
    week_monday_et,
)


class PdtGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_max_day_trades_always_five(self) -> None:
        self.assertEqual(max_day_trades_per_week(5_000), 5)
        self.assertEqual(max_day_trades_per_week(24_999.99), 5)
        self.assertEqual(max_day_trades_per_week(25_000), 5)
        self.assertEqual(max_day_trades_per_week(100_000), 5)

    def test_week_monday(self) -> None:
        self.assertEqual(week_monday_et("2026-11-04"), date(2026, 11, 2))
        self.assertEqual(week_monday_et(date(2026, 11, 2)), date(2026, 11, 2))

    def test_allows_five_then_blocks_sixth(self) -> None:
        equity = 5_000.0
        days = [
            "2026-11-02",
            "2026-11-03",
            "2026-11-04",
            "2026-11-05",
            "2026-11-06",
        ]
        for i, d in enumerate(days):
            gate = can_open_day_trade(self.conn, equity=equity, session_date=d)
            self.assertTrue(gate["allowed"], gate)
            self.assertEqual(gate["cap"], 5)
            record_day_trade(
                self.conn,
                session_date=d,
                ticker="AAA",
                equity_at_trade=equity,
            )
            self.conn.commit()
            self.assertEqual(count_day_trades_in_week(self.conn, d), i + 1)

        blocked = can_open_day_trade(self.conn, equity=equity, session_date="2026-11-07")
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["used"], 5)
        self.assertIn("weekly_cap_reached_5", blocked["reason"] or "")

    def test_new_week_resets_counter(self) -> None:
        equity = 5_000.0
        for d in ["2026-11-02", "2026-11-03", "2026-11-04"]:
            record_day_trade(
                self.conn, session_date=d, ticker="X", equity_at_trade=equity
            )
        self.conn.commit()
        gate = can_open_day_trade(self.conn, equity=equity, session_date="2026-11-09")
        self.assertTrue(gate["allowed"])
        self.assertEqual(gate["used"], 0)
        self.assertEqual(gate["week_start_et"], "2026-11-09")

    def test_duplicate_session_rejected(self) -> None:
        record_day_trade(
            self.conn,
            session_date="2026-11-02",
            ticker="IRM",
            equity_at_trade=5_000,
        )
        self.conn.commit()
        gate = can_open_day_trade(
            self.conn, equity=5_000, session_date="2026-11-02"
        )
        self.assertFalse(gate["allowed"])
        self.assertTrue(gate["already_recorded_today"])


if __name__ == "__main__":
    unittest.main()
