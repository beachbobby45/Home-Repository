"""Random-pick control using the same 5m fill engine as paper_sim.

Compares #1 ranked pick vs a seeded random ticker from the ranked top-N
over a historical window. Results persist in app_settings for the scoreboard.
"""

from __future__ import annotations

import json
import random
import sqlite3
from datetime import date
from typing import Any

from investment_agent.account import get_setting, set_setting
from investment_agent.backtest import _group_bars_by_date
from investment_agent.close_report import (
    _day_bar,
    build_ranked_top20_for_date,
    get_rank_snapshot,
)
from investment_agent.execution.paper_sim import resolve_fill_mode, simulate_round_trip_5m
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
)
from investment_agent.period_screener import list_trading_dates
from investment_agent.providers.yfinance_bars import get_intraday_bars
from investment_agent.pullback_entry import compute_pullback_trade_plan

RANDOM_CONTROL_SETTING_KEY = "paper_random_control_summary"
DEFAULT_SINCE = "2026-10-20"
DEFAULT_TOP_N = 20
DEFAULT_DEPLOY = 5_000.0
PAPER_SOURCE = "random_control"


def _avg_range(conn: sqlite3.Connection, ticker: str, row: dict) -> float | None:
    if row.get("avg_range_pct") is not None:
        try:
            return float(row["avg_range_pct"])
        except (TypeError, ValueError):
            pass
    m = conn.execute(
        """
        SELECT avg_range_pct FROM ticker_metrics
        WHERE ticker = ?
        ORDER BY computed_at DESC LIMIT 1
        """,
        (ticker,),
    ).fetchone()
    if m and m["avg_range_pct"] is not None:
        return float(m["avg_range_pct"])
    return None


def _ranked_for_day(conn: sqlite3.Connection, session_date: str, top_n: int) -> list[dict]:
    snap = get_rank_snapshot(conn, session_date)
    if snap:
        return list(snap)[:top_n]
    return build_ranked_top20_for_date(conn, session_date)[:top_n]


def _simulate_pick(
    conn: sqlite3.Connection,
    *,
    session_date: str,
    row: dict,
    deploy: float,
    fill_mode: str,
    bars_cache: dict[str, dict[str, list[dict]]],
    lookback_days: int,
) -> dict[str, Any]:
    ticker = str(row.get("ticker") or "").upper()
    base: dict[str, Any] = {
        "ticker": ticker or None,
        "filled": False,
        "complete": True,
        "net_pnl": None,
        "counts": False,
        "scenario": None,
        "detail": None,
    }
    if not ticker:
        base["detail"] = "missing ticker"
        return base

    bar = _day_bar(conn, ticker, session_date)
    if not bar:
        base["detail"] = "no daily bar"
        return base

    avg_range = _avg_range(conn, ticker, row)
    if avg_range is None:
        base["detail"] = "no avg_range_pct"
        return base

    plan = compute_pullback_trade_plan(
        session_open=float(bar["open"]),
        avg_range_pct=avg_range,
        deploy_dollar=deploy,
        net_target=daily_profit_target(deploy),
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
    )
    if not plan:
        base["detail"] = "empty pullback plan"
        return base

    if ticker not in bars_cache:
        try:
            raw = get_intraday_bars(ticker, lookback_days=lookback_days, interval="5m")
            bars_cache[ticker] = _group_bars_by_date(raw)
        except Exception as exc:  # noqa: BLE001
            bars_cache[ticker] = {}
            base["detail"] = f"5m fetch failed: {exc}"
            return base

    day_bars = list(bars_cache[ticker].get(session_date[:10], []))
    sim = simulate_round_trip_5m(
        day_bars,
        buy=float(plan["limit_buy_price"]),
        sell=float(plan["limit_sell_price"]),
        stop=float(plan["stop_price"]),
        shares=int(plan["shares"]),
        buy_fee=DEFAULT_BUY_FEE,
        sell_fee=DEFAULT_SELL_FEE,
        as_of_et=None,
        fill_mode=fill_mode,
    )
    net = sim.get("net_pnl")
    counts = sim.get("complete") and net is not None and sim.get("scenario") != "no_5m_bars"
    return {
        "ticker": ticker,
        "filled": bool(sim.get("filled")),
        "complete": bool(sim.get("complete")),
        "net_pnl": net,
        "counts": bool(counts),
        "scenario": sim.get("scenario"),
        "detail": sim.get("detail"),
        "fill_mode": sim.get("fill_mode") or fill_mode,
        "entry_price": plan["limit_buy_price"],
        "shares": plan["shares"],
    }


def get_random_control_summary(conn: sqlite3.Connection) -> dict[str, Any] | None:
    raw = get_setting(conn, RANDOM_CONTROL_SETTING_KEY, "")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def save_random_control_summary(conn: sqlite3.Connection, summary: dict[str, Any]) -> None:
    set_setting(conn, RANDOM_CONTROL_SETTING_KEY, json.dumps(summary))


def run_random_pick_control(
    conn: sqlite3.Connection,
    *,
    since: str = DEFAULT_SINCE,
    until: str | None = None,
    top_n: int = DEFAULT_TOP_N,
    deploy: float = DEFAULT_DEPLOY,
    fill_mode: str | None = None,
    seed: int = 42,
    lookback_days: int = 60,
    persist: bool = True,
) -> dict[str, Any]:
    """Run #1 vs random-from-top-N control over trading days in [since, until]."""
    mode = resolve_fill_mode(fill_mode)
    until = (until or date.today().isoformat())[:10]
    since = since[:10]
    # Pull enough calendar sessions; filter to window
    all_dates = list_trading_dates(conn, count=120, end_date=until)
    dates = [d for d in all_dates if since <= d <= until]
    dates.sort()

    rng = random.Random(seed)
    bars_cache: dict[str, dict[str, list[dict]]] = {}
    days_out: list[dict[str, Any]] = []
    top1_nets: list[float] = []
    rand_nets: list[float] = []

    for day in dates:
        ranked = _ranked_for_day(conn, day, top_n)
        if len(ranked) < 2:
            days_out.append(
                {
                    "session_date_et": day,
                    "skipped": True,
                    "reason": f"need ≥2 ranked names, got {len(ranked)}",
                }
            )
            continue

        top1 = ranked[0]
        # Random from top-N excluding #1 so control is a true alternate pick
        pool = ranked[1:]
        pick = rng.choice(pool)

        top_sim = _simulate_pick(
            conn,
            session_date=day,
            row=top1,
            deploy=deploy,
            fill_mode=mode,
            bars_cache=bars_cache,
            lookback_days=lookback_days,
        )
        rand_sim = _simulate_pick(
            conn,
            session_date=day,
            row=pick,
            deploy=deploy,
            fill_mode=mode,
            bars_cache=bars_cache,
            lookback_days=lookback_days,
        )
        if top_sim.get("counts") and top_sim.get("net_pnl") is not None:
            top1_nets.append(float(top_sim["net_pnl"]))
        if rand_sim.get("counts") and rand_sim.get("net_pnl") is not None:
            rand_nets.append(float(rand_sim["net_pnl"]))

        days_out.append(
            {
                "session_date_et": day,
                "skipped": False,
                "top1": top_sim,
                "random": rand_sim,
                "ranked_n": len(ranked),
            }
        )

    def _stats(nets: list[float]) -> dict[str, Any]:
        if not nets:
            return {
                "sessions_counted": 0,
                "total_net_pnl": 0.0,
                "expectancy": None,
                "fills": 0,
            }
        return {
            "sessions_counted": len(nets),
            "total_net_pnl": round(sum(nets), 2),
            "expectancy": round(sum(nets) / len(nets), 4),
            "fills": len(nets),
        }

    top_stats = _stats(top1_nets)
    rand_stats = _stats(rand_nets)
    comparable = bool(
        top_stats["expectancy"] is not None and rand_stats["expectancy"] is not None
    )
    beats = None
    if comparable:
        beats = float(top_stats["expectancy"]) > float(rand_stats["expectancy"])

    summary: dict[str, Any] = {
        "ok": True,
        "window": {"since": since, "until": until},
        "top_n": top_n,
        "deploy": deploy,
        "fill_mode": mode,
        "seed": seed,
        "days_evaluated": len([d for d in days_out if not d.get("skipped")]),
        "days_skipped": len([d for d in days_out if d.get("skipped")]),
        "top1": top_stats,
        "random": rand_stats,
        "beats_random": beats,
        "random_control_ok": beats,
        "updated_at": date.today().isoformat(),
        "source": PAPER_SOURCE,
    }

    if persist:
        # Persist compact summary (not every day row) for scoreboard
        save_random_control_summary(conn, {**summary, "days": days_out[-40:]})

    summary["days"] = days_out
    return summary
