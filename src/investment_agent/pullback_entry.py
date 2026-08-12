"""Pullback limit entry — buy in lower half of expected daily swing, sell at Growth Plan target."""

from __future__ import annotations

from datetime import time

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.strategy import STOP_PCT

# Limit buy ≈ open minus this fraction of the 20d avg daily range (2–4% band).
PULLBACK_RANGE_FRACTION = 0.35
PULLBACK_MIN_PCT = 0.25
PULLBACK_MAX_PCT = 1.20
LIMIT_FILL_DEADLINE = time(11, 30)
LIMIT_FILL_DEADLINE_LABEL = "11:30 ET"


def pullback_pct_from_open(avg_range_pct: float) -> float:
    """Percent below session open for the limit buy."""
    if avg_range_pct <= 0:
        return PULLBACK_MIN_PCT
    raw = avg_range_pct * PULLBACK_RANGE_FRACTION
    return max(PULLBACK_MIN_PCT, min(raw, PULLBACK_MAX_PCT))


def limit_buy_price(session_open: float, avg_range_pct: float) -> float:
    if session_open <= 0:
        return 0.0
    pct = pullback_pct_from_open(avg_range_pct)
    return round(session_open * (1 - pct / 100), 2)


def dollar_confidence(dollar_hit_rate_pct: float) -> str:
    if dollar_hit_rate_pct >= 50.0:
        return "high"
    if dollar_hit_rate_pct >= 40.0:
        return "medium"
    return "low"


def compute_pullback_trade_plan(
    *,
    session_open: float,
    avg_range_pct: float,
    deploy_dollar: float,
    net_target: float | None = None,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    stop_pct: float = STOP_PCT,
) -> dict:
    """Limit-buy entry in the lower part of the expected swing + Growth Plan sell/stop."""
    if session_open <= 0 or deploy_dollar <= 0:
        return {}
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    pullback_pct = pullback_pct_from_open(avg_range_pct)
    entry = limit_buy_price(session_open, avg_range_pct)
    if entry <= 0:
        return {}
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return {}
    stop_px = round(entry * (1 - stop_pct / 100), 2)
    target_px = round(
        sell_price_for_net_target(
            entry_price=entry,
            shares=shares,
            net_target=goal,
            buy_fee=buy_fee,
            sell_fee=sell_fee,
        ),
        2,
    )
    notional = round(shares * entry, 2)
    total_cost = round(notional + buy_fee, 2)
    net_at_target = round(shares * (target_px - entry) - buy_fee - sell_fee, 2)
    net_at_stop = round(shares * (stop_px - entry) - buy_fee - sell_fee, 2)
    est_high = session_open * (1 + (avg_range_pct / 2) / 100) if avg_range_pct > 0 else session_open * 1.015
    net_at_est_high = round(shares * (est_high - entry) - buy_fee - sell_fee, 2)
    return {
        "entry_mode": "pullback_limit",
        "session_open": round(session_open, 2),
        "pullback_pct": round(pullback_pct, 2),
        "limit_buy_price": entry,
        "entry_price": entry,
        "recommended_entry": entry,
        "limit_sell_price": target_px,
        "target_price": target_px,
        "stop_price": stop_px,
        "shares": shares,
        "recommended_shares": shares,
        "notional": notional,
        "total_cost": total_cost,
        "target_pct": round(target_move_pct(entry, target_px), 2),
        "stop_pct": stop_pct,
        "net_target": round(goal, 2),
        "net_at_target": net_at_target,
        "net_at_stop": net_at_stop,
        "estimated_net_at_typical_high": net_at_est_high,
        "fees_round_trip": round_trip_fees(buy_fee, sell_fee),
        "limit_fill_deadline_et": LIMIT_FILL_DEADLINE_LABEL,
        "skip_if_not_filled_by": LIMIT_FILL_DEADLINE_LABEL,
        "avg_range_pct": round(avg_range_pct, 2),
    }


def simulate_pullback_dollar_outcome(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    avg_range_pct: float,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> str:
    """Daily-bar sim: limit buy in pullback zone, then target/stop from fill price."""
    if open_px <= 0:
        return "invalid"
    entry = limit_buy_price(open_px, avg_range_pct)
    if entry <= 0:
        return "invalid"
    if low > entry:
        return "no_fill"
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return "invalid"
    target_px = sell_price_for_net_target(
        entry_price=entry,
        shares=shares,
        net_target=goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    stop_px = entry * (1 - stop_pct / 100)
    if high >= target_px:
        return "target"
    if low <= stop_px:
        return "stop"
    return "neither"


def net_at_high_after_pullback_fill(
    open_px: float,
    high: float,
    low: float,
    *,
    deploy_dollar: float,
    avg_range_pct: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
) -> float:
    """Net at day high if limit filled; else 0."""
    if open_px <= 0 or low <= 0:
        return 0.0
    entry = limit_buy_price(open_px, avg_range_pct)
    if low > entry:
        return 0.0
    shares = int((deploy_dollar - buy_fee) / entry)
    if shares <= 0:
        return 0.0
    return round(shares * (high - entry) - buy_fee - sell_fee, 2)


def limit_fill_missed(
    *,
    limit_buy_price: float,
    session_low: float | None,
    as_of_time: time,
) -> bool:
    """True after the fill deadline if the session low never reached the limit buy."""
    if as_of_time <= LIMIT_FILL_DEADLINE:
        return False
    if limit_buy_price <= 0 or session_low is None:
        return False
    return session_low > limit_buy_price
