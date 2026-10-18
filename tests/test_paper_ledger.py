"""Internal paper ledger + dual-arm session logging."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.paper_ledger import (
    ACCOUNT_ALL,
    ACCOUNT_GATE,
    apply_round_trip,
    ensure_paper_accounts,
    get_paper_balance,
    next_trading_day_et,
    paper_scoreboard,
    settle_due_cash,
)
from investment_agent.execution.paper_sim import simulate_round_trip_5m
from investment_agent.finance import DEFAULT_BUY_FEE, DEFAULT_SELL_FEE


class PaperLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)
        ensure_paper_accounts(self.conn, starting_cash=5_000)
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_accounts_seeded(self) -> None:
        g = get_paper_balance(self.conn, ACCOUNT_GATE)
        a = get_paper_balance(self.conn, ACCOUNT_ALL)
        self.assertEqual(g["settled_cash"], 5_000)
        self.assertEqual(a["settled_cash"], 5_000)

    def test_t1_settlement(self) -> None:
        self.assertEqual(next_trading_day_et("2026-10-16"), "2026-10-19")  # Fri → Mon
        applied = apply_round_trip(
            self.conn,
            account_name=ACCOUNT_GATE,
            session_date_et="2026-10-16",
            ticker="TEST",
            shares=10,
            entry_price=100.0,
            exit_price=101.0,
            buy_fee=DEFAULT_BUY_FEE,
            sell_fee=DEFAULT_SELL_FEE,
            fill_ts="2026-10-16T10:00:00-04:00",
            exit_ts="2026-10-16T11:00:00-04:00",
        )
        self.conn.commit()
        bal = get_paper_balance(self.conn, ACCOUNT_GATE)
        # Buy spent settled; sale in unsettled
        self.assertLess(bal["settled_cash"], 5_000)
        self.assertGreater(bal["unsettled_cash"], 0)
        self.assertEqual(applied["settle_on_et"], "2026-10-19")

        settle_due_cash(self.conn, session_date_et="2026-10-19", account_name=ACCOUNT_GATE)
        self.conn.commit()
        bal2 = get_paper_balance(self.conn, ACCOUNT_GATE)
        self.assertEqual(bal2["unsettled_cash"], 0.0)
        self.assertAlmostEqual(bal2["equity"], bal["equity"], places=2)

    def test_sim_fill_and_target(self) -> None:
        bars = [
            {"ts": "2026-10-16T09:35:00-04:00", "open": 100, "high": 100.5, "low": 99.0, "close": 99.5},
            {"ts": "2026-10-16T10:00:00-04:00", "open": 99.5, "high": 102.0, "low": 99.4, "close": 101.5},
        ]
        # Explicit touch keeps legacy assertion; default fill_mode is trade_through
        # (also fills here because low 99.0 < buy 99.5).
        sim = simulate_round_trip_5m(
            bars,
            buy=99.5,
            sell=101.0,
            stop=98.5,
            shares=10,
            buy_fee=7,
            sell_fee=7,
            as_of_et=None,
            fill_mode="touch",
        )
        self.assertTrue(sim["filled"])
        self.assertTrue(sim["complete"])
        self.assertEqual(sim["exit_reason"], "target")

    def test_scoreboard_structure(self) -> None:
        sb = paper_scoreboard(self.conn)
        self.assertEqual(sb["primary_arm"], ACCOUNT_GATE)
        self.assertIn(ACCOUNT_ALL, sb["arms"])
        self.assertIn("checks", sb)


class PaperApiTests(unittest.TestCase):
    def test_paper_status_endpoint(self) -> None:
        import sqlite3

        from fastapi.testclient import TestClient

        from investment_agent.dashboard.app import app

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_db(db_path)

            def fake_connect():
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                return conn

            with patch("investment_agent.dashboard.app.connect", fake_connect):
                with patch("investment_agent.dashboard.app.init_db", lambda: db_path):
                    http = TestClient(app)
                    r = http.get("/api/paper/status")
                    self.assertEqual(r.status_code, 200, r.text)
                    body = r.json()
                    self.assertEqual(body["execution_mode"], "paper")
                    self.assertIn("gate_approved", body["balances"])
                    sb = http.get("/api/paper/scoreboard")
                    self.assertEqual(sb.status_code, 200)


if __name__ == "__main__":
    unittest.main()
