"""Armed plan persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from investment_agent.db import connect, init_db
from investment_agent.execution.armed_plan import (
    AllocationMode,
    ArmedLeg,
    ArmedPlan,
    PlanStatus,
    get_armed_plan_for_session,
    save_armed_plan,
    set_armed_plan_status,
)
from investment_agent.execution.pdt_guard import can_open_day_trade


class ArmedPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        init_db(self.db)
        self.conn = connect(self.db)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_save_and_load_single_top1(self) -> None:
        gate = can_open_day_trade(self.conn, equity=5_000, session_date="2026-11-02")
        plan = ArmedPlan(
            session_date_et="2026-11-02",
            allocation_mode=AllocationMode.SINGLE_TOP1,
            status=PlanStatus.PROPOSED,
            legs=[
                ArmedLeg(
                    rank=1,
                    ticker="IRM",
                    limit_buy=125.60,
                    limit_sell=129.81,
                    stop=124.97,
                    shares=39,
                    deploy=5_000,
                    avg_range_pct=3.0,
                )
            ],
            equity_snapshot=5_000,
            pdt_cap=gate["cap"],
            pdt_used=gate["used"],
            allow_trade=False,
            ma_score=45,
            day_gate_mode="preserve",
        )
        pid = save_armed_plan(self.conn, plan)
        self.conn.commit()
        self.assertIsInstance(pid, int)

        loaded = get_armed_plan_for_session(self.conn, "2026-11-02")
        assert loaded is not None
        self.assertEqual(loaded.allocation_mode, AllocationMode.SINGLE_TOP1)
        self.assertEqual(loaded.status, PlanStatus.PROPOSED)
        self.assertEqual(loaded.legs[0].ticker, "IRM")
        self.assertEqual(loaded.pdt_cap, 3)

        set_armed_plan_status(self.conn, loaded.plan_uuid, PlanStatus.ARMED)
        self.conn.commit()
        again = get_armed_plan_for_session(self.conn, "2026-11-02")
        assert again is not None
        self.assertEqual(again.status, PlanStatus.ARMED)

    def test_broker_tables_exist(self) -> None:
        tables = {
            r[0]
            for r in self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        for name in (
            "broker_accounts",
            "broker_balances",
            "broker_positions",
            "broker_orders",
            "broker_fills",
            "armed_plans",
            "pdt_day_trades",
        ):
            self.assertIn(name, tables)


if __name__ == "__main__":
    unittest.main()
