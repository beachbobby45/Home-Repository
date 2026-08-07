"""Dollar-target prediction — Growth Plan $ net goal from historical open→high.

Uses daily OHLCV bars with **open as entry proxy** (same as period screener and
intraday backtest). Deploy size and net target follow ``daily_profit_target()``.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
)
from investment_agent.strategy import STOP_PCT

# Minimum historical open→high hit rate to treat as reliably reachable (ranking / caution)
MIN_DOLLAR_HIT_RATE_PCT = 30.0
# Expected net at typical day-high must reach this fraction of today's goal for GO
MIN_EXPECTED_NET_RATIO = 0.95
DEFAULT_LOOKBACK_DAYS = 14


@dataclass(frozen=True)
class DollarDayBar:
    open: float
    high: float
    low: float


def shares_for_deploy(
    entry_price: float,
    deploy_dollar: float,
    *,
    buy_fee: float = DEFAULT_BUY_FEE,
) -> int:
    if entry_price <= 0 or deploy_dollar <= buy_fee:
        return 0
    return int((deploy_dollar - buy_fee) / entry_price)


def net_pnl_at_price(
    *,
    entry_price: float,
    exit_price: float,
    shares: int,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    if shares <= 0 or entry_price <= 0:
        return 0.0
    return round(shares * (exit_price - entry_price) - buy_fee - sell_fee, 2)


def target_sell_price(
    *,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float | None:
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = shares_for_deploy(entry_price, deploy_dollar, buy_fee=buy_fee)
    if shares <= 0 or goal <= 0:
        return None
    return sell_price_for_net_target(
        entry_price=entry_price,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )


def simulate_dollar_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> str:
    """Daily-bar approximation: did open→high reach the Growth Plan sell price?"""
    if open_px <= 0:
        return "invalid"
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = shares_for_deploy(open_px, deploy_dollar, buy_fee=buy_fee)
    if shares <= 0:
        return "invalid"
    target_px = sell_price_for_net_target(
        entry_price=open_px,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    stop_px = open_px * (1 - stop_pct / 100)
    if high >= target_px:
        return "target"
    if low <= stop_px:
        return "stop"
    return "neither"


def net_at_high_from_open(
    open_px: float,
    high: float,
    *,
    deploy_dollar: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    shares = shares_for_deploy(open_px, deploy_dollar, buy_fee=buy_fee)
    return net_pnl_at_price(
        entry_price=open_px,
        exit_price=high,
        shares=shares,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )


def estimate_net_at_typical_high(
    entry_price: float,
    avg_range_pct: float,
    *,
    deploy_dollar: float,
    net_target: float | None = None,
) -> float:
    """Estimate net if price reaches open + half the typical daily range (upside leg)."""
    if entry_price <= 0 or avg_range_pct <= 0:
        return 0.0
    est_high = entry_price * (1 + (avg_range_pct / 2) / 100)
    return net_at_high_from_open(
        entry_price,
        est_high,
        deploy_dollar=deploy_dollar,
    )


@dataclass
class DollarHistoryStats:
    days_evaluated: int
    dollar_targets: int
    dollar_stops: int
    dollar_neither: int
    dollar_hit_rate_pct: float
    avg_net_at_high: float
    median_net_at_high: float
    max_net_at_high: float
    min_net_at_high: float

    def to_dict(self) -> dict:
        return {
            "days_evaluated": self.days_evaluated,
            "dollar_targets": self.dollar_targets,
            "dollar_stops": self.dollar_stops,
            "dollar_neither": self.dollar_neither,
            "dollar_hit_rate_pct": self.dollar_hit_rate_pct,
            "avg_net_at_high": self.avg_net_at_high,
            "median_net_at_high": self.median_net_at_high,
            "max_net_at_high": self.max_net_at_high,
            "min_net_at_high": self.min_net_at_high,
        }


def evaluate_dollar_history(
    bars: list[DollarDayBar],
    *,
    deploy_dollar: float,
    net_target: float | None = None,
) -> DollarHistoryStats:
    """Simulate Growth Plan outcomes on historical daily bars (open entry)."""
    targets = stops = neither = 0
    nets: list[float] = []

    for bar in bars:
        if bar.open <= 0:
            continue
        outcome = simulate_dollar_outcome(
            bar.open,
            bar.high,
            bar.low,
            deploy_dollar=deploy_dollar,
            net_target=net_target,
        )
        if outcome == "target":
            targets += 1
        elif outcome == "stop":
            stops += 1
        elif outcome == "neither":
            neither += 1
        else:
            continue
        nets.append(
            net_at_high_from_open(bar.open, bar.high, deploy_dollar=deploy_dollar)
        )

    days = len(nets)
    decided = targets + stops
    hit_rate = round(100.0 * targets / max(decided, 1), 1) if decided else 0.0

    if nets:
        sorted_nets = sorted(nets)
        mid = len(sorted_nets) // 2
        median = (
            sorted_nets[mid]
            if len(sorted_nets) % 2
            else (sorted_nets[mid - 1] + sorted_nets[mid]) / 2
        )
        return DollarHistoryStats(
            days_evaluated=days,
            dollar_targets=targets,
            dollar_stops=stops,
            dollar_neither=neither,
            dollar_hit_rate_pct=hit_rate,
            avg_net_at_high=round(sum(nets) / days, 2),
            median_net_at_high=round(median, 2),
            max_net_at_high=round(max(nets), 2),
            min_net_at_high=round(min(nets), 2),
        )

    return DollarHistoryStats(
        days_evaluated=0,
        dollar_targets=0,
        dollar_stops=0,
        dollar_neither=0,
        dollar_hit_rate_pct=0.0,
        avg_net_at_high=0.0,
        median_net_at_high=0.0,
        max_net_at_high=0.0,
        min_net_at_high=0.0,
    )


def assess_dollar_reachability(
    *,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
    history: DollarHistoryStats | None = None,
) -> dict:
    """Predict whether today's $ goal is reachable from this entry using history."""
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    fees = round_trip_fees()
    shares = shares_for_deploy(entry_price, deploy_dollar)
    target_px = target_sell_price(
        entry_price=entry_price,
        deploy_dollar=deploy_dollar,
        net_target=goal,
    )

    expected_net = None
    if avg_range_pct is not None and avg_range_pct > 0:
        expected_net = estimate_net_at_typical_high(
            entry_price,
            avg_range_pct,
            deploy_dollar=deploy_dollar,
            net_target=goal,
        )

    hist_avg = history.avg_net_at_high if history and history.days_evaluated else None
    hist_hit = history.dollar_hit_rate_pct if history and history.days_evaluated else None

    blockers: list[str] = []
    cautions: list[str] = []
    checks: list[dict] = []

    def add(name: str, ok: bool | None, message: str) -> None:
        checks.append({"name": name, "ok": ok, "message": message})

    if expected_net is not None:
        ratio = expected_net / goal if goal > 0 else 0.0
        if ratio < MIN_EXPECTED_NET_RATIO:
            blockers.append(
                f"Typical day high nets ~${expected_net:.0f} from this entry "
                f"(need ${goal:.0f}) — range too tight for Growth Plan"
            )
            add(
                "Expected net at typical high",
                False,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal ({ratio:.0%})",
            )
        elif ratio < 1.0:
            cautions.append(
                f"Typical high only ~${expected_net:.0f} net — marginal for ${goal:.0f}"
            )
            add(
                "Expected net at typical high",
                None,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal",
            )
        else:
            add(
                "Expected net at typical high",
                True,
                f"~${expected_net:.0f} at avg swing high vs ${goal:.0f} goal",
            )

    if hist_avg is not None and hist_hit is not None:
        add(
            "Historical net at high",
            True if hist_avg >= goal * MIN_EXPECTED_NET_RATIO else None,
            f"Avg ${hist_avg:.0f} net at day high over {history.days_evaluated}d "
            f"({hist_hit:.0f}% hit ${goal:.0f})",
        )
        if hist_hit < MIN_DOLLAR_HIT_RATE_PCT and hist_avg < goal * MIN_EXPECTED_NET_RATIO:
            blockers.append(
                f"Historical open→high hit ${goal:.0f} only {hist_hit:.0f}% of days "
                f"(avg net ${hist_avg:.0f} at high)"
            )
            checks[-1]["ok"] = False
        elif hist_hit < MIN_DOLLAR_HIT_RATE_PCT:
            cautions.append(
                f"Historical ${goal:.0f} hit rate only {hist_hit:.0f}% — lower confidence"
            )

    if blockers:
        verdict = "NOT_REACHABLE"
        headline = f"Unlikely to reach ${goal:.0f} net from this entry"
        detail = blockers[0]
    elif cautions:
        verdict = "MARGINAL"
        headline = f"Marginal for ${goal:.0f} net — history suggests tight upside"
        detail = cautions[0]
    else:
        verdict = "REACHABLE"
        headline = f"Historical range supports ${goal:.0f} net goal"
        detail = (
            f"Typical high ~${expected_net:.0f} net"
            if expected_net is not None
            else f"{hist_hit:.0f}% historical hit rate" if hist_hit is not None else "OK"
        )

    return {
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "blockers": blockers,
        "cautions": cautions,
        "net_target": goal,
        "expected_net_at_typical_high": expected_net,
        "historical_avg_net_at_high": hist_avg,
        "dollar_hit_rate_pct": hist_hit,
        "dollar_history_days": history.days_evaluated if history else 0,
        "target_sell_price": round(target_px, 2) if target_px else None,
        "shares": shares,
        "fees_round_trip": fees,
    }


def load_dollar_history(
    conn: sqlite3.Connection,
    ticker: str,
    *,
    end_date: str | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    deploy_dollar: float,
    net_target: float | None = None,
) -> DollarHistoryStats:
    """Load recent daily bars and evaluate open→high dollar outcomes."""
    from investment_agent.db import get_ohlcv_bars

    end = end_date or datetime.now().strftime("%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    start = (end_dt - timedelta(days=lookback_days * 2)).strftime("%Y-%m-%d")
    rows = get_ohlcv_bars(conn, ticker.upper(), start_date=start, end_date=end)
    if not rows:
        return evaluate_dollar_history([], deploy_dollar=deploy_dollar, net_target=net_target)

    history_rows = [r for r in rows if r["date"] < end][-lookback_days:]
    bars = [
        DollarDayBar(
            open=float(r["open"]),
            high=float(r["high"]),
            low=float(r["low"]),
        )
        for r in history_rows
        if r["open"] and r["high"] and r["low"]
    ]
    return evaluate_dollar_history(bars, deploy_dollar=deploy_dollar, net_target=net_target)
