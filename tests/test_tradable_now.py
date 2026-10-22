"""Unit tests for top-3 soft tradable-now scorer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.execution.tradable_now import (
    select_best_tradable,
    session_vwap,
    sma,
    score_limit_reachability,
    score_trend_ma,
    score_volume_expansion,
)


def _bar(ts: str, o: float, h: float, l: float, c: float, v: int) -> dict:
    return {
        "ts": ts,
        "date": ts[:10],
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "volume": v,
    }


class TradableNowUnitTests(unittest.TestCase):
    def test_sma_and_vwap(self) -> None:
        self.assertEqual(sma([1, 2, 3, 4], 3), 3.0)
        self.assertIsNone(sma([1, 2], 3))
        bars = [
            _bar("2026-10-22T09:35:00-04:00", 10, 11, 9, 10, 100),
            _bar("2026-10-22T09:40:00-04:00", 10, 12, 10, 11, 300),
        ]
        # typical1=10, typical2=11; vwap = (10*100 + 11*300)/400 = 10.75
        self.assertAlmostEqual(session_vwap(bars) or 0, 10.75, places=4)

    def test_trend_prefers_above_ma_or_vwap(self) -> None:
        score, above_30, above_v = score_trend_ma(
            last_price=110, sma_30d=100, vwap=105
        )
        self.assertGreater(score, 0.8)
        self.assertTrue(above_30)
        self.assertTrue(above_v)
        low, a30, av = score_trend_ma(last_price=90, sma_30d=100, vwap=105)
        self.assertLess(low, 0.3)
        self.assertFalse(a30)
        self.assertFalse(av)

    def test_volume_expansion(self) -> None:
        quiet = [_bar(f"2026-10-22T09:{30+i:02d}:00-04:00", 10, 10.5, 9.5, 10, 100) for i in range(20)]
        loud = [_bar(f"2026-10-22T11:{i:02d}:00-04:00", 10, 10.5, 9.5, 10, 250) for i in range(6)]
        score, expanding = score_volume_expansion(quiet + loud)
        self.assertTrue(expanding)
        self.assertGreater(score, 0.6)

    def test_reachability_hit_vs_far(self) -> None:
        hit_bars = [_bar("2026-10-22T10:00:00-04:00", 100, 101, 98.5, 99, 1000)]
        self.assertEqual(score_limit_reachability(hit_bars, limit_buy=99.0), 1.0)
        far_bars = [_bar("2026-10-22T10:00:00-04:00", 105, 106, 104.5, 105, 1000)]
        self.assertLess(score_limit_reachability(far_bars, limit_buy=99.0), 0.3)

    def test_select_prefers_reachable_name_over_prep_rank(self) -> None:
        candidates = [
            {
                "ticker": "AAA",
                "prep_rank": 1,
                "limit_buy_price": 100.0,
                "limit_sell_price": 103.0,
                "stop_price": 99.0,
                "recommended_shares": 10,
                "deploy": 1000,
            },
            {
                "ticker": "BBB",
                "prep_rank": 2,
                "limit_buy_price": 50.0,
                "limit_sell_price": 52.0,
                "stop_price": 49.5,
                "recommended_shares": 20,
                "deploy": 1000,
            },
        ]
        # AAA never near limit; BBB trades through + above MA + volume
        aaa_bars = [
            _bar("2026-10-22T10:00:00-04:00", 104, 105, 103.5, 104, 100) for _ in range(30)
        ]
        bbb_base = [
            _bar(f"2026-10-22T09:{30+i:02d}:00-04:00", 51, 51.5, 50.8, 51, 80)
            for i in range(20)
        ]
        bbb_live = [
            _bar("2026-10-22T10:05:00-04:00", 50.5, 51, 49.8, 50.2, 200),
            _bar("2026-10-22T10:10:00-04:00", 50.2, 50.8, 50.0, 50.6, 220),
            _bar("2026-10-22T10:15:00-04:00", 50.6, 51.2, 50.4, 51.0, 240),
            _bar("2026-10-22T10:20:00-04:00", 51.0, 51.5, 50.7, 51.2, 260),
            _bar("2026-10-22T10:25:00-04:00", 51.2, 51.8, 50.9, 51.5, 280),
            _bar("2026-10-22T10:30:00-04:00", 51.5, 52.0, 51.0, 51.8, 300),
        ]
        daily_bbb = [{"close": 48.0 + i * 0.1} for i in range(35)]  # rising into above 30d
        daily_aaa = [{"close": 100.0} for _ in range(35)]

        result = select_best_tradable(
            candidates,
            bars_5m_by_ticker={"AAA": aaa_bars, "BBB": bbb_base + bbb_live},
            daily_by_ticker={"AAA": daily_aaa, "BBB": daily_bbb},
        )
        self.assertIsNotNone(result.winner)
        assert result.winner is not None
        self.assertEqual(result.winner.ticker, "BBB")
        self.assertGreater(result.winner.composite, result.scored[1].composite)

    def test_tie_breaks_to_better_prep_rank(self) -> None:
        candidates = [
            {
                "ticker": "ONE",
                "prep_rank": 1,
                "limit_buy_price": 10.0,
                "limit_sell_price": 10.5,
                "stop_price": 9.9,
                "shares": 5,
                "deploy": 50,
            },
            {
                "ticker": "TWO",
                "prep_rank": 2,
                "limit_buy_price": 10.0,
                "limit_sell_price": 10.5,
                "stop_price": 9.9,
                "shares": 5,
                "deploy": 50,
            },
        ]
        # Identical empty bars → neutral metrics; rank 1 wins
        result = select_best_tradable(
            candidates,
            bars_5m_by_ticker={},
            daily_by_ticker={},
        )
        assert result.winner is not None
        self.assertEqual(result.winner.ticker, "ONE")


if __name__ == "__main__":
    unittest.main()
