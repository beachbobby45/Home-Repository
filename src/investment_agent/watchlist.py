"""Watchlist management — presets, import, universe stats (Phase 7)."""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from investment_agent.account import set_setting
from investment_agent.db import get_active_watchlist
from investment_agent.ingest import DEFAULT_TICKERS
from investment_agent.liquidity import SWING_TARGET_PCT
from investment_agent.step3_status import (
    STEP3_STATUS_LABELS,
    classify_step3_status,
    swing_band_high,
    swing_band_low,
)
from investment_agent.strategy import REGIME_ONLY_TICKERS

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_DIR = REPO_ROOT / "universe"

PRESETS: dict[str, str] = {
    "starter10": "Starter 10 (default ingest list)",
    "sp100": "S&P 100 liquid subset (~100 tickers)",
    "sp500": "S&P 500 full index (~500 tickers + regime ETFs)",
    "datacenter_us": "US AI data center buildout & maintenance (~96 tickers)",
}

SPECIAL_WATCH_EXTRAS_PREFIX = "special_watch_extras:"
_TICKER_RE = re.compile(r"^[A-Z]{1,6}$")


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
    name = preset_name.lower().strip()
    if name not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {preset_name!r}. Choose one of: {known}")
    if name == "starter10" and not (UNIVERSE_DIR / "starter10.txt").is_file():
        return [t.upper() for t in DEFAULT_TICKERS]
    path = UNIVERSE_DIR / f"{name}.txt"
    return load_tickers_from_file(path)


def _special_watch_extras_key(preset_name: str) -> str:
    return f"{SPECIAL_WATCH_EXTRAS_PREFIX}{preset_name.lower().strip()}"


def get_special_watch_extras(conn: sqlite3.Connection, preset_name: str) -> list[str]:
    """Manually added tickers for a Special Watch preset (stored in app_settings)."""
    key = _special_watch_extras_key(preset_name)
    row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    if not row:
        return []
    try:
        data = json.loads(row["value"])
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    seen: set[str] = set()
    out: list[str] = []
    for item in data:
        t = str(item).strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _save_special_watch_extras(
    conn: sqlite3.Connection, preset_name: str, tickers: list[str]
) -> None:
    set_setting(conn, _special_watch_extras_key(preset_name), json.dumps(tickers))


def merge_special_watch_tickers(preset_name: str, extras: list[str]) -> list[str]:
    """Preset file tickers plus manual extras (deduped, preset order first)."""
    base = load_preset_tickers(preset_name)
    seen = set(base)
    out = list(base)
    for ticker in extras:
        t = ticker.upper()
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def add_special_watch_ticker(
    conn: sqlite3.Connection,
    preset_name: str,
    ticker: str,
) -> dict:
    """Add a ticker to Special Watch and the active watchlist (metrics on next ingest)."""
    name = preset_name.lower().strip()
    if name not in PRESETS:
        known = ", ".join(sorted(PRESETS))
        raise ValueError(f"Unknown preset {preset_name!r}. Choose one of: {known}")

    t = ticker.strip().upper()
    if not t or not _TICKER_RE.match(t):
        raise ValueError(f"Invalid ticker symbol {ticker!r} — use 1–6 letters (e.g. NBIS)")

    preset_tickers = set(load_preset_tickers(name))
    extras = get_special_watch_extras(conn, name)
    added_to_extras = False
    if t not in preset_tickers and t not in extras:
        extras.append(t)
        _save_special_watch_extras(conn, name, extras)
        added_to_extras = True

    upsert_tickers(conn, [t], source="special_watch", added_via=f"{name}_manual")
    return {
        "ok": True,
        "preset": name,
        "ticker": t,
        "added_to_extras": added_to_extras,
        "already_in_preset": t in preset_tickers,
        "tickers_activated": 1,
    }


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
    from investment_agent.screen_actions import PRESET_ACTIONS, record_screen_action

    action_id = PRESET_ACTIONS.get(preset_name.lower().strip())
    if action_id:
        record_screen_action(
            conn,
            action_id,
            detail=f"{len(tickers)} tickers loaded, {added} activated",
        )
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


def _parse_iso_age_hours(iso_ts: str | None) -> float | None:
    if not iso_ts:
        return None
    try:
        from datetime import datetime, timezone

        ts = iso_ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 3600.0
    except ValueError:
        return None


def compute_data_freshness(conn: sqlite3.Connection) -> dict:
    """How old quotes and metrics are for the active watchlist."""
    active = get_active_watchlist(conn)
    if not active:
        return {
            "quotes_newest_at": None,
            "quotes_oldest_at": None,
            "quotes_max_age_hours": None,
            "metrics_newest_at": None,
            "metrics_max_age_hours": None,
            "stale_quote_count": 0,
            "stale_metrics_count": 0,
        }

    placeholders = ",".join("?" for _ in active)
    quote_rows = conn.execute(
        f"""
        SELECT ticker, MAX(captured_at) AS last_at
        FROM quotes
        WHERE ticker IN ({placeholders})
        GROUP BY ticker
        """,
        active,
    ).fetchall()
    metric_rows = conn.execute(
        f"""
        SELECT ticker, MAX(computed_at) AS last_at
        FROM ticker_metrics
        WHERE ticker IN ({placeholders})
        GROUP BY ticker
        """,
        active,
    ).fetchall()

    quote_times = [r["last_at"] for r in quote_rows if r["last_at"]]
    metric_times = [r["last_at"] for r in metric_rows if r["last_at"]]
    quote_ages = [_parse_iso_age_hours(t) for t in quote_times]
    metric_ages = [_parse_iso_age_hours(t) for t in metric_times]
    quote_ages_valid = [a for a in quote_ages if a is not None]
    metric_ages_valid = [a for a in metric_ages if a is not None]

    newest_quote = max(quote_times) if quote_times else None
    oldest_quote = min(quote_times) if quote_times else None
    newest_metric = max(metric_times) if metric_times else None

    return {
        "quotes_newest_at": newest_quote,
        "quotes_oldest_at": oldest_quote,
        "quotes_max_age_hours": round(max(quote_ages_valid), 1) if quote_ages_valid else None,
        "metrics_newest_at": newest_metric,
        "metrics_max_age_hours": round(max(metric_ages_valid), 1) if metric_ages_valid else None,
        "stale_quote_count": sum(1 for a in quote_ages_valid if a >= 4.0),
        "stale_metrics_count": sum(1 for a in metric_ages_valid if a >= 24.0),
        "tickers_with_quotes": len(quote_times),
        "tickers_with_metrics": len(metric_times),
    }


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
        "freshness": compute_data_freshness(conn),
    }


def _latest_metrics_by_ticker(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = conn.execute(
        """
        SELECT m.*
        FROM ticker_metrics m
        INNER JOIN (
          SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
        ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
        """
    ).fetchall()
    return {row["ticker"]: row for row in rows}


def build_special_watch_report(
    conn: sqlite3.Connection,
    preset_name: str = "datacenter_us",
) -> dict:
    """Status for every ticker in a thematic preset — Step 3 pass / too quiet / too wild / etc."""
    name = preset_name.lower().strip()
    extras = get_special_watch_extras(conn, name)
    tickers = merge_special_watch_tickers(name, extras)
    active = set(get_active_watchlist(conn))
    metrics = _latest_metrics_by_ticker(conn)

    rows: list[dict] = []
    counts: dict[str, int] = {k: 0 for k in STEP3_STATUS_LABELS}

    for ticker in tickers:
        regime_only = ticker in REGIME_ONLY_TICKERS
        m = metrics.get(ticker)
        if m is None:
            status = classify_step3_status(ticker=ticker, regime_only=regime_only)
            row = {
                "ticker": ticker,
                "step3_status": status,
                "step3_label": STEP3_STATUS_LABELS[status],
                "avg_range_pct": None,
                "adv_dollar": None,
                "adv_dollar_m": None,
                "meets_liquidity": None,
                "near_swing_target": None,
                "in_active_watchlist": ticker in active,
            }
        else:
            avg_range = float(m["avg_range_pct"] or 0)
            adv = float(m["adv_dollar"] or 0)
            meets_liq = bool(m["meets_liquidity_min"])
            near_swing = bool(m["near_swing_target"])
            status = classify_step3_status(
                ticker=ticker,
                meets_liquidity=meets_liq,
                near_swing=near_swing,
                avg_range_pct=avg_range,
                regime_only=regime_only,
            )
            row = {
                "ticker": ticker,
                "step3_status": status,
                "step3_label": STEP3_STATUS_LABELS[status],
                "avg_range_pct": round(avg_range, 2),
                "adv_dollar": round(adv, 0),
                "adv_dollar_m": round(adv / 1_000_000, 1) if adv else 0.0,
                "meets_liquidity": meets_liq,
                "near_swing_target": near_swing,
                "in_active_watchlist": ticker in active,
            }
        counts[status] = counts.get(status, 0) + 1
        rows.append(row)

    with_metrics = sum(1 for r in rows if r["step3_status"] != "missing_metrics")
    return {
        "preset": name,
        "description": PRESETS.get(name, name),
        "ticker_count": len(tickers),
        "preset_ticker_count": len(load_preset_tickers(name)),
        "manual_ticker_count": len(extras),
        "with_metrics": with_metrics,
        "missing_metrics": len(tickers) - with_metrics,
        "step3_pass": counts.get("step3_pass", 0),
        "too_quiet": counts.get("too_quiet", 0),
        "too_wild": counts.get("too_wild", 0),
        "low_liquidity": counts.get("low_liquidity", 0),
        "status_counts": counts,
        "swing_band_pct": {
            "target": SWING_TARGET_PCT,
            "low": swing_band_low(),
            "high": swing_band_high(),
        },
        "tickers": rows,
    }
