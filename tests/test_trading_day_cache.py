"""Trading-day status short TTL cache — keeps dashboard polls snappy."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.db import connect, init_db
from investment_agent import trading_day_cache as cache_mod


class TradingDayCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "t.db"
        self.conn = connect(init_db(self.db))
        cache_mod.clear_trading_day_status_cache()
        self._n = 0

        def _fake_build(_conn):
            self._n += 1
            return {"verdict": "GO", "build_n": self._n, "headline": f"build-{self._n}"}

        self._build_patch = patch.object(
            cache_mod, "build_trading_day_status", side_effect=_fake_build
        )
        self._build_patch.start()

    def tearDown(self) -> None:
        self._build_patch.stop()
        cache_mod.clear_trading_day_status_cache()
        self.conn.close()
        self.tmp.cleanup()

    def test_second_call_is_cache_hit(self) -> None:
        a = cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        b = cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        self.assertEqual(self._n, 1)
        self.assertFalse(a["_cache"]["hit"])
        self.assertTrue(b["_cache"]["hit"])
        self.assertEqual(a["build_n"], b["build_n"])

    def test_force_refresh_rebuilds(self) -> None:
        cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        c = cache_mod.get_trading_day_status_cached(
            self.conn, force_refresh=True, ttl_sec=60
        )
        self.assertEqual(self._n, 2)
        self.assertFalse(c["_cache"]["hit"])
        self.assertEqual(c["build_n"], 2)

    def test_expiry_rebuilds(self) -> None:
        cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=0.01)
        # Expire by rewriting entry clock
        with cache_mod._lock:
            assert cache_mod._entry is not None
            cache_mod._entry["expires_at"] = 0.0
        d = cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        self.assertEqual(self._n, 2)
        self.assertFalse(d["_cache"]["hit"])

    def test_clear_cache(self) -> None:
        cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        cache_mod.clear_trading_day_status_cache()
        e = cache_mod.get_trading_day_status_cached(self.conn, ttl_sec=60)
        self.assertEqual(self._n, 2)
        self.assertFalse(e["_cache"]["hit"])


if __name__ == "__main__":
    unittest.main()
