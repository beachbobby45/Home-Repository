"""Ops audit TEST rows must not affect paper P&L."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent.execution.ops_audit import (
    KIND_TEST,
    get_ledger_source,
    list_audit_events,
    log_test_suite_results,
)
from investment_agent.execution.paper_ledger import (
    ACCOUNT_GATE,
    ensure_paper_accounts,
    get_paper_balance,
)


class OpsAuditTests(unittest.TestCase):
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

    def test_ensure_paper_accounts_activates_paper_ledger(self) -> None:
        # setUp calls ensure_paper_accounts, which flips ledger_source to paper
        # so Risk/Account tabs use the paper book (not an empty journal).
        self.assertEqual(get_ledger_source(self.conn), "paper")

    def test_fresh_db_defaults_ledger_to_journal(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        try:
            db = Path(tmp.name) / "fresh.db"
            init_db(db)
            conn = connect(db)
            self.assertEqual(get_ledger_source(conn), "journal")
            conn.close()
        finally:
            tmp.cleanup()

    def test_test_suite_does_not_change_equity(self) -> None:
        before = get_paper_balance(self.conn, ACCOUNT_GATE)
        log_test_suite_results(
            self.conn,
            suite_name="unit",
            passed=10,
            failed=0,
            total=10,
            notes="fixture",
        )
        self.conn.commit()
        after = get_paper_balance(self.conn, ACCOUNT_GATE)
        self.assertEqual(before["equity"], after["equity"])
        self.assertEqual(before["settled_cash"], after["settled_cash"])
        events = list_audit_events(self.conn, kind=KIND_TEST, limit=5)
        self.assertTrue(events)
        self.assertFalse(events[0]["affects_pnl"])
        self.assertIn("PASS", events[0]["title"])


if __name__ == "__main__":
    unittest.main()
