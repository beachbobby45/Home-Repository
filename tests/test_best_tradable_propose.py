"""Propose + paper wiring for best_tradable_top3 vs #1 shadow."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import set_setting
from investment_agent.db import connect, init_db
from investment_agent.execution.armed_plan import AllocationMode, get_armed_plan_for_session
from investment_agent.execution.paper_ledger import ACCOUNT_ALL, ACCOUNT_GATE, ensure_paper_accounts
from investment_agent.execution.paper_runner import run_paper_tick
from investment_agent.execution import paper_runner
from investment_agent.execution.propose import (
    ALLOCATION_MODE_KEY,
    DEFAULT_ALLOCATION_MODE,
    get_allocation_mode,
    propose_armed_plan,
)


def _pick(ticker: str, buy: float, *, rank: int = 1) -> dict:
    return {
        "ticker": ticker,
        "prep_rank": rank,
        "limit_buy_price": buy,
        "limit_sell_price": buy * 1.02,
        "stop_price": buy * 0.99,
        "recommended_shares": 10,
        "deploy": buy * 10,
        "avg_range_pct": 2.5,
        "source": f"ranked_#{rank}",
    }


class BestTradableProposeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        ensure_paper_accounts(self.conn, starting_cash=5_000.0)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmp.cleanup()

    def test_default_allocation_mode_is_best_tradable_top3(self) -> None:
        self.assertEqual(DEFAULT_ALLOCATION_MODE, AllocationMode.BEST_TRADABLE_TOP3)
        self.assertEqual(get_allocation_mode(self.conn), AllocationMode.BEST_TRADABLE_TOP3)

    def test_propose_selects_higher_score_not_always_rank1(self) -> None:
        cands = [_pick("AAA", 100.0, rank=1), _pick("BBB", 50.0, rank=2)]
        status = {
            "top_pick": cands[0],
            "second_pick": cands[1],
            "market_activity": {"allow_trade": True, "score": 70},
            "allow_trade": True,
        }
        # Inject bars so BBB is clearly more tradable-now
        from investment_agent.execution.tradable_now import select_best_tradable

        bars = {
            "AAA": [
                {
                    "ts": "2026-10-22T10:00:00-04:00",
                    "open": 104,
                    "high": 105,
                    "low": 103.5,
                    "close": 104,
                    "volume": 100,
                }
            ]
            * 30,
            "BBB": [
                {
                    "ts": f"2026-10-22T09:{30+i:02d}:00-04:00",
                    "open": 51,
                    "high": 51.2,
                    "low": 50.8,
                    "close": 51,
                    "volume": 80,
                }
                for i in range(20)
            ]
            + [
                {
                    "ts": "2026-10-22T10:10:00-04:00",
                    "open": 50.5,
                    "high": 51,
                    "low": 49.7,
                    "close": 50.5,
                    "volume": 300,
                }
            ],
        }
        daily = {
            "AAA": [{"close": 100.0}] * 35,
            "BBB": [{"close": 48.0 + i * 0.05} for i in range(35)],
        }
        sel = select_best_tradable(cands, bars_5m_by_ticker=bars, daily_by_ticker=daily)
        self.assertEqual(sel.winner.ticker if sel.winner else None, "BBB")

        with (
            patch(
                "investment_agent.execution.propose.collect_propose_candidates",
                return_value=(cands, status),
            ),
            patch(
                "investment_agent.execution.propose.can_open_day_trade",
                return_value={"allowed": True, "cap": 5, "used": 0, "reason": None},
            ),
            patch(
                "investment_agent.execution.propose.resolve_equity_for_pdt",
                return_value=5_000.0,
            ),
            patch(
                "investment_agent.execution.propose.build_dashboard_summary",
            ) as summ,
        ):
            summ.return_value.tradable_cash = 5_000.0
            out = propose_armed_plan(
                self.conn,
                session_date_et="2026-10-22",
                bars_5m_by_ticker=bars,
                daily_by_ticker=daily,
            )
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["plan"]["legs"][0]["ticker"], "BBB")
        self.assertEqual(out["plan"]["allocation_mode"], "best_tradable_top3")
        self.assertIn("selection_audit", out["plan"])

    def test_single_top1_mode_still_uses_top_pick(self) -> None:
        set_setting(self.conn, ALLOCATION_MODE_KEY, AllocationMode.SINGLE_TOP1.value)
        status = {
            "top_pick": _pick("PLTR", 187.0),
            "market_activity": {"allow_trade": False, "score": 40},
        }
        with (
            patch(
                "investment_agent.execution.propose.build_trading_day_status",
                return_value=status,
            ),
            patch(
                "investment_agent.execution.propose.can_open_day_trade",
                return_value={"allowed": True, "cap": 5, "used": 0, "reason": None},
            ),
            patch(
                "investment_agent.execution.propose.resolve_equity_for_pdt",
                return_value=5_000.0,
            ),
            patch(
                "investment_agent.execution.propose.build_dashboard_summary",
            ) as summ,
        ):
            summ.return_value.tradable_cash = 5_000.0
            out = propose_armed_plan(self.conn, session_date_et="2026-10-22")
        self.assertTrue(out["ok"])
        self.assertEqual(out["plan"]["legs"][0]["ticker"], "PLTR")
        self.assertEqual(out["plan"]["allocation_mode"], "single_top1")

    def test_shadow_persist_false_does_not_overwrite_primary_plan(self) -> None:
        cands = [_pick("AAA", 100.0, rank=1), _pick("BBB", 50.0, rank=2)]
        status = {
            "top_pick": cands[0],
            "second_pick": cands[1],
            "market_activity": {"allow_trade": True, "score": 70},
        }
        bars = {
            "AAA": [
                {
                    "ts": "2026-10-22T10:00:00-04:00",
                    "open": 104,
                    "high": 105,
                    "low": 103.5,
                    "close": 104,
                    "volume": 50,
                }
            ]
            * 25,
            "BBB": [
                {
                    "ts": "2026-10-22T10:00:00-04:00",
                    "open": 50,
                    "high": 50.5,
                    "low": 49.5,
                    "close": 50.2,
                    "volume": 400,
                }
            ]
            * 25,
        }
        daily = {"AAA": [{"close": 100}] * 35, "BBB": [{"close": 49 + i * 0.05} for i in range(35)]}
        with (
            patch(
                "investment_agent.execution.propose.collect_propose_candidates",
                return_value=(cands, status),
            ),
            patch(
                "investment_agent.execution.propose.build_trading_day_status",
                return_value=status,
            ),
            patch(
                "investment_agent.execution.propose.can_open_day_trade",
                return_value={"allowed": True, "cap": 5, "used": 0, "reason": None},
            ),
            patch(
                "investment_agent.execution.propose.resolve_equity_for_pdt",
                return_value=5_000.0,
            ),
            patch(
                "investment_agent.execution.propose.build_dashboard_summary",
            ) as summ,
        ):
            summ.return_value.tradable_cash = 5_000.0
            primary = propose_armed_plan(
                self.conn,
                session_date_et="2026-10-22",
                allocation_mode=AllocationMode.BEST_TRADABLE_TOP3,
                bars_5m_by_ticker=bars,
                daily_by_ticker=daily,
            )
            shadow = propose_armed_plan(
                self.conn,
                session_date_et="2026-10-22",
                allocation_mode=AllocationMode.SINGLE_TOP1,
                persist=False,
            )
        self.assertTrue(primary["ok"])
        self.assertTrue(shadow["ok"])
        self.assertFalse(shadow.get("persisted"))
        stored = get_armed_plan_for_session(self.conn, "2026-10-22")
        assert stored is not None
        self.assertEqual(stored.allocation_mode, AllocationMode.BEST_TRADABLE_TOP3)
        self.assertEqual(stored.legs[0].ticker, primary["plan"]["legs"][0]["ticker"])
        self.assertEqual(shadow["plan"]["legs"][0]["ticker"], "AAA")

    def test_paper_tick_uses_distinct_primary_and_shadow_signals(self) -> None:
        primary = {
            "ok": True,
            "session_date_et": "2026-10-22",
            "ticker": "BBB",
            "limit_buy": 50.0,
            "limit_sell": 52.0,
            "stop": 49.5,
            "shares": 20,
            "deploy": 1000.0,
            "allow_trade": True,
            "ma_score": 70,
            "day_gate_mode": "produce",
            "allocation_mode": "best_tradable_top3",
            "selection": {"winner": {"ticker": "BBB"}},
        }
        shadow = {
            **primary,
            "ticker": "AAA",
            "limit_buy": 100.0,
            "limit_sell": 103.0,
            "stop": 99.0,
            "shares": 10,
            "allocation_mode": "single_top1",
            "selection": {"winner": {"ticker": "AAA"}},
        }
        calls: list[str] = []

        def fake_plan(conn, day, **kwargs):
            mode = kwargs.get("allocation_mode")
            mode_s = mode.value if hasattr(mode, "value") else str(mode)
            calls.append(mode_s)
            return primary if "best_tradable" in mode_s else shadow

        bars = [
            {
                "ts": "2026-10-22T10:00:00-04:00",
                "open": 50,
                "high": 51,
                "low": 49.4,
                "close": 50.5,
                "volume": 1000,
            },
            {
                "ts": "2026-10-22T15:55:00-04:00",
                "open": 51,
                "high": 52.5,
                "low": 50.8,
                "close": 52.1,
                "volume": 1000,
            },
        ]
        with (
            patch.object(paper_runner, "is_kill_switch_active", return_value=False),
            patch.object(paper_runner, "get_allocation_mode", return_value=AllocationMode.BEST_TRADABLE_TOP3),
            patch.object(paper_runner, "_plan_signal", side_effect=fake_plan),
            patch.object(paper_runner, "_fetch_day_bars", return_value=bars),
        ):
            out = run_paper_tick(
                self.conn, session_date_et="2026-10-22", force_complete=True
            )
        self.assertTrue(out["ok"])
        self.assertEqual(out["signal"]["ticker"], "BBB")
        self.assertEqual(out["shadow_signal"]["ticker"], "AAA")
        self.assertIn(AllocationMode.BEST_TRADABLE_TOP3.value, calls)
        self.assertIn(AllocationMode.SINGLE_TOP1.value, calls)
        # Gate book should reference BBB; all_signals AAA
        from investment_agent.execution.paper_ledger import get_session_log

        gate = get_session_log(self.conn, "2026-10-22", ACCOUNT_GATE)
        all_arm = get_session_log(self.conn, "2026-10-22", ACCOUNT_ALL)
        assert gate and all_arm
        self.assertEqual(gate.get("ticker"), "BBB")
        self.assertEqual(all_arm.get("ticker"), "AAA")


if __name__ == "__main__":
    unittest.main()
