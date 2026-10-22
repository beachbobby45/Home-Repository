"""Broker sync stub — fixture → SQLite mirror."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from investment_agent.broker.client import (
    BrokerAccountSnapshot,
    StubBrokerClient,
    fixture_paper_snapshot,
)
from investment_agent.broker.sync import (
    latest_broker_balance,
    sync_account_snapshot,
    sync_from_client,
)
from investment_agent.db import connect, init_db
from investment_agent.execution.propose import resolve_equity_for_pdt


class BrokerSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_fixture_sync_and_idempotent_fills(self) -> None:
        snap = BrokerAccountSnapshot(
            external_account_id="rh-1",
            equity=5_250.0,
            cash=5_250.0,
            buying_power=5_250.0,
            positions=[{"ticker": "IRM", "qty": 0, "avg_cost": 0}],
            open_orders=[
                {
                    "id": "ord-1",
                    "ticker": "IRM",
                    "side": "buy",
                    "status": "open",
                    "limit_price": 125.6,
                    "qty": 39,
                }
            ],
            fills=[
                {
                    "id": "fill-1",
                    "ticker": "IRM",
                    "side": "buy",
                    "qty": 39,
                    "price": 125.6,
                    "fee": 0,
                    "session_date_et": "2026-11-02",
                }
            ],
            is_paper=True,
        )
        r1 = sync_account_snapshot(self.conn, snap, session_date_et="2026-11-02")
        self.conn.commit()
        self.assertTrue(r1["ok"])
        self.assertEqual(r1["fills_upserted"], 1)

        r2 = sync_account_snapshot(self.conn, snap, session_date_et="2026-11-02")
        self.conn.commit()
        self.assertEqual(r2["fills_upserted"], 1)

        n_fills = self.conn.execute("SELECT COUNT(*) AS n FROM broker_fills").fetchone()["n"]
        self.assertEqual(n_fills, 1)

        bal = latest_broker_balance(self.conn)
        assert bal is not None
        self.assertEqual(bal["equity"], 5_250.0)
        self.assertAlmostEqual(resolve_equity_for_pdt(self.conn), 5_250.0)

    def test_stub_client_sync(self) -> None:
        client = StubBrokerClient(fixture_paper_snapshot(equity=10_000, cash=10_000))
        out = sync_from_client(self.conn, client)
        self.conn.commit()
        self.assertEqual(out["equity"], 10_000)


if __name__ == "__main__":
    unittest.main()
