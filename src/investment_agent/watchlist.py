"""Watchlist management — presets, import, universe stats (Phase 7)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from investment_agent.db import get_active_watchlist
from investment_agent.ingest import DEFAULT_TICKERS
from investment_agent.strategy import REGIME_ONLY_TICKERS

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_DIR = REPO_ROOT / "universe"

PRESETS: dict[str, str] = {
    "starter10": "Starter 10 (default ingest list)",
    "sp100": "S&P 100 liquid subset (~100 tickers)",
    "sp500": "S&P 500 full index (~500 tickers + regime ETFs)",
}


@dataclass(frozen=True)
class PresetInfo:
    name: str
    description: str
    ticker_count: int
    path: Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def list_presets() -> list[PresetInfo]:
    items: list[PresetInfo] = []
    for name, desc in PRESETS.items():
        path = UNIVERSE_DIR / f"{name}.txt"
        tickers = load_tickers_from_file(path) if path.is_file() else []
        items.append(PresetInfo(name=name, description=desc, ticker_count=len(tickers), path=path))
    return items


def load_tickers_from_file(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Universe file not found: {path}")
    tickers: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tickers.append(line.upper())
    # preserve order, dedupe
    seen: set[str] = set()
    out: list[str] = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def load_preset_tickers(preset_name: str) -> list[str]:
    name = preset_name.lower()
    if name == "starter10" and not (UNIVERSE_DIR / "starter10.txt").is_file():
        return [t.upper() for t in DEFAULT_TICKERS]
    path = UNIVERSE_DIR / f"{name}.txt"
    return load_tickers_from_file(path)


def get_active_watchlist_details(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        """
        SELECT ticker, sector, active, source, added_via, added_at
        FROM watchlist
        WHERE active = 1
        ORDER BY ticker
        """
    ).fetchall()
    return [dict(row) for row in rows]


def load_preset_into_watchlist(
    conn: sqlite3.Connection,
    preset_name: str,
    *,
    replace: bool = False,
) -> dict:
    tickers = load_preset_tickers(preset_name)
    if replace:
        conn.execute("UPDATE watchlist SET active = 0")
    added = upsert_tickers(conn, tickers, source="preset", added_via=preset_name)
    return {
        "ok": True,
        "preset": preset_name,
        "tickers_loaded": len(tickers),
        "tickers_activated": added,
        "replace": replace,
    }


def import_tickers(
    conn: sqlite3.Connection,
    tickers: list[str],
    *,
    source: str = "import",
    added_via: str = "manual",
) -> dict:
    normalized = [t.strip().upper() for t in tickers if t.strip()]
    added = upsert_tickers(conn, normalized, source=source, added_via=added_via)
    return {"ok": True, "tickers_received": len(normalized), "tickers_activated": added}


def deactivate_ticker(conn: sqlite3.Connection, ticker: str) -> dict:
    cur = conn.execute(
        "UPDATE watchlist SET active = 0 WHERE ticker = ?",
        (ticker.upper(),),
    )
    return {"ok": cur.rowcount > 0, "ticker": ticker.upper()}


def upsert_tickers(
    conn: sqlite3.Connection,
    tickers: list[str],
    *,
    source: str = "manual",
    added_via: str = "manual",
) -> int:
    now = _utc_now()
    count = 0
    for ticker in tickers:
        t = ticker.upper()
        conn.execute(
            """
            INSERT INTO watchlist (ticker, active, source, added_via, added_at)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
              active = 1,
              source = excluded.source,
              added_via = excluded.added_via
            """,
            (t, source, added_via, now),
        )
        count += 1
    return count


def compute_universe_stats(conn: sqlite3.Connection) -> dict:
    """Step 3 pass/filter counts from latest ticker_metrics per active ticker."""
    rows = conn.execute(
        """
        SELECT m.ticker, m.meets_liquidity_min, m.near_swing_target, m.avg_range_pct
        FROM ticker_metrics m
        INNER JOIN watchlist w ON w.ticker = m.ticker AND w.active = 1
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        ORDER BY m.ticker
        """
    ).fetchall()

    active = get_active_watchlist(conn)
    universe_size = len(active)
    with_metrics = len(rows)
    pass_liq = sum(1 for r in rows if r["meets_liquidity_min"])
    pass_swing = sum(1 for r in rows if r["near_swing_target"])
    pass_both = sum(
        1
        for r in rows
        if r["meets_liquidity_min"]
        and r["near_swing_target"]
        and r["ticker"] not in REGIME_ONLY_TICKERS
    )
    tradeable = sum(1 for t in active if t not in REGIME_ONLY_TICKERS)
    filtered_out = max(tradeable - pass_both, 0)

    return {
        "universe_size": universe_size,
        "tradeable_universe": tradeable,
        "with_metrics": with_metrics,
        "pass_liquidity": pass_liq,
        "pass_swing": pass_swing,
        "pass_both_step3": pass_both,
        "filtered_out": filtered_out,
        "filter_pct_out": round(100.0 * filtered_out / max(tradeable, 1), 1),
        "pass_pct": round(100.0 * pass_both / max(tradeable, 1), 1),
        "missing_metrics": max(universe_size - with_metrics, 0),
    }
