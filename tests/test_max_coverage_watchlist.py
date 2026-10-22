"""Max-coverage preset: S&P 500 ∪ unique datacenter_us."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, get_active_watchlist, init_db
from investment_agent.watchlist import (
    MAX_COVERAGE_PRESET,
    PRESETS,
    build_sp500_datacenter_tickers,
    list_presets,
    load_preset_into_watchlist,
    load_preset_tickers,
    max_coverage_breakdown,
)


class MaxCoverageWatchlistTests(unittest.TestCase):
    def test_preset_registered(self) -> None:
        self.assertIn(MAX_COVERAGE_PRESET, PRESETS)
        names = {p.name for p in list_presets()}
        self.assertIn(MAX_COVERAGE_PRESET, names)

    def test_union_is_sp500_plus_datacenter_only(self) -> None:
        from investment_agent.watchlist import load_tickers_from_file, UNIVERSE_DIR

        sp = set(load_tickers_from_file(UNIVERSE_DIR / "sp500.txt"))
        dc = load_tickers_from_file(UNIVERSE_DIR / "datacenter_us.txt")
        union = build_sp500_datacenter_tickers()
        self.assertEqual(union, load_preset_tickers(MAX_COVERAGE_PRESET))
        self.assertGreater(len(union), len(sp))
        # Every S&P name present; order starts with S&P list
        self.assertTrue(sp.issubset(set(union)))
        for t in dc:
            self.assertIn(t, union)
        breakdown = max_coverage_breakdown()
        self.assertEqual(breakdown["union_count"], len(union))
        self.assertEqual(
            breakdown["datacenter_only_count"],
            len([t for t in dc if t not in sp]),
        )
        # Not the naive sum of all four presets (~700)
        self.assertLess(len(union), 700)

    def test_load_replace_activates_union(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        db = Path(tmp.name) / "t.db"
        conn = connect(init_db(db))
        # Seed a tiny active list first
        load_preset_into_watchlist(conn, "starter10", replace=True)
        conn.commit()
        before = set(get_active_watchlist(conn))
        self.assertLess(len(before), 50)

        result = load_preset_into_watchlist(conn, MAX_COVERAGE_PRESET, replace=True)
        conn.commit()
        self.assertTrue(result["ok"])
        self.assertGreaterEqual(result["tickers_loaded"], 500)
        active = get_active_watchlist(conn)
        expected = set(build_sp500_datacenter_tickers())
        self.assertEqual(set(active), expected)
        self.assertGreater(len(active), 500)
        conn.close()


if __name__ == "__main__":
    unittest.main()
