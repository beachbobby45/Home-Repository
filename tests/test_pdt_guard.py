"""PDT weekly frequency guard."""

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

    def test_max_day_trades_threshold(self) -> None:
        self.assertEqual(max_day_trades_per_week(5_000), 3)
        self.assertEqual(max_day_trades_per_week(24_999.99), 3)
        self.assertEqual(max_day_trades_per_week(25_000), 5)
        self.assertEqual(max_day_trades_per_week(100_000), 5)

    def test_week_monday(self) -> None:
        # 2026-11-04 is Wednesday
        self.assertEqual(week_monday_et("2026-11-04"), date(2026, 11, 2))
        self.assertEqual(week_monday_et(date(2026, 11, 2)), date(2026, 11, 2))

    def test_blocks_fourth_trade_under_25k(self) -> None:
        equity = 10_000.0
        days = ["2026-11-02", "2026-11-03", "2026-11-04"]
        for i, d in enumerate(days):
            gate = can_open_day_trade(self.conn, equity=equity, session_date=d)
            self.assertTrue(gate["allowed"], gate)
            self.assertEqual(gate["cap"], 3)
            record_day_trade(
                self.conn,
                session_date=d,
                ticker="AAA",
                equity_at_trade=equity,
            )
            self.conn.commit()
            self.assertEqual(count_day_trades_in_week(self.conn, d), i + 1)

        blocked = can_open_day_trade(self.conn, equity=equity, session_date="2026-11-05")
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["used"], 3)
        self.assertIn("weekly_cap_reached_3", blocked["reason"] or "")
        with self.assertRaises(ValueError):
            record_day_trade(
                self.conn,
                session_date="2026-11-05",
                ticker="BBB",
                equity_at_trade=equity,
            )

    def test_allows_five_at_or_above_25k(self) -> None:
        equity = 25_000.0
        days = [
            "2026-11-02",
            "2026-11-03",
            "2026-11-04",
            "2026-11-05",
            "2026-11-06",
        ]
        for d in days:
            gate = can_open_day_trade(self.conn, equity=equity, session_date=d)
            self.assertTrue(gate["allowed"], gate)
            self.assertEqual(gate["cap"], 5)
            record_day_trade(
                self.conn,
                session_date=d,
                ticker="PLTR",
                equity_at_trade=equity,
            )
            self.conn.commit()

        blocked = can_open_day_trade(self.conn, equity=equity, session_date="2026-11-07")
        # 2026-11-07 is Saturday — still same week Mon Nov 2
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["used"], 5)

    def test_new_week_resets_counter(self) -> None:
        equity = 5_000.0
        for d in ["2026-11-02", "2026-11-03", "2026-11-04"]:
            record_day_trade(
                self.conn, session_date=d, ticker="X", equity_at_trade=equity
            )
        self.conn.commit()
        # Next Monday
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
