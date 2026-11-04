"""Short TTL cache for expensive trading-day status builds.

Ops/paper paths should not wait on a full trading-day rebuild every poll.
Manual refresh (?refresh=1 or POST /api/trading-day/refresh) bypasses the cache.
"""

from __future__ import annotations

import threading
import time
from typing import Any

import sqlite3

from investment_agent.trading_day import build_trading_day_status

# Sweet spot: snappy UI, still fresh enough for intraday decisions.
DEFAULT_TTL_SEC = 45.0

_lock = threading.Lock()
_entry: dict[str, Any] | None = None


def cache_ttl_sec() -> float:
    return DEFAULT_TTL_SEC


def clear_trading_day_status_cache() -> None:
    global _entry
    with _lock:
        _entry = None


def get_trading_day_status_cached(
    conn: sqlite3.Connection,
    *,
    force_refresh: bool = False,
    ttl_sec: float | None = None,
) -> dict[str, Any]:
    """Return trading-day status, serving a recent build when still fresh."""
    global _entry
    ttl = DEFAULT_TTL_SEC if ttl_sec is None else float(ttl_sec)
    now = time.monotonic()

    with _lock:
        if (
            not force_refresh
            and _entry is not None
            and now < float(_entry["expires_at"])
            and isinstance(_entry.get("payload"), dict)
        ):
            hit = dict(_entry["payload"])
            meta = dict(hit.get("_cache") or {})
            meta.update(
                {
                    "hit": True,
                    "ttl_sec": ttl,
                    "age_sec": round(now - float(_entry["built_mono"]), 3),
                    "built_at_mono": _entry["built_mono"],
                }
            )
            hit["_cache"] = meta
            return hit

    # Build outside the lock so concurrent callers don't serialize on Finnhub/DB work
    # after a miss — first finisher wins the cache slot.
    payload = build_trading_day_status(conn)
    built_mono = time.monotonic()
    payload["_cache"] = {
        "hit": False,
        "ttl_sec": ttl,
        "age_sec": 0.0,
        "built_at_mono": built_mono,
    }
    with _lock:
        _entry = {
            "payload": payload,
            "built_mono": built_mono,
            "expires_at": built_mono + max(ttl, 0.0),
        }
    return payload
