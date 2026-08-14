"""Intraday tradability — can we reach the Growth Plan $ target from *this* entry?

Uses Finnhub live quote fields already stored in ``quotes`` (price, open, high, low,
prev_close). No intraday candles or paid APIs required.
"""

from __future__ import annotations

import sqlite3

from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.dollar_target import DollarHistoryStats, assess_dollar_reachability
from investment_agent.strategy import STOP_PCT

# Gap-and-chase filters (from Aug 2026 week review — NFLX Wed gap)
MAX_GAP_UP_PCT = 1.0
MAX_GAP_DOWN_PCT = 1.5
MAX_CHASE_ABOVE_OPEN_PCT = 0.50
MIN_SESSION_RANGE_PCT = 0.40
MIN_NET_AT_DAY_HIGH_RATIO = 0.95
TARGET_RETRACE_TOLERANCE = 0.998


def _apply_risk_engine(
    result: dict,
    *,
    conn: sqlite3.Connection,
    ticker: str | None,
    block_new_longs: bool,
) -> dict:
    """Merge portfolio-level Risk Engine checks into tradability output."""
    plan = result.get("plan") or {}
    if not plan.get("entry_price"):
        return result

    from investment_agent.risk_engine import (
        MarketSnapshot,
        build_portfolio_snapshot,
        evaluate_proposal_from_plan_dict,
        risk_decision_to_dict,
    )

    portfolio = build_portfolio_snapshot(conn)
    market = MarketSnapshot(block_new_longs=block_new_longs)
    risk = evaluate_proposal_from_plan_dict(
        plan=plan,
        ticker=(ticker or "—").upper(),
        portfolio=portfolio,
        market=market,
    )
    result["risk"] = risk_decision_to_dict(risk)
    for check in risk.checks:
        result["checks"].append(
            {
                "name": f"Risk: {check['name']}",
                "ok": check["ok"],
                "message": check["message"],
            }
        )
    if risk.verdict == "rejected":
        result["verdict"] = "NOT_TRADABLE"
        result["blockers"] = list(result.get("blockers") or []) + list(risk.blockers)
        if risk.blockers:
            result["headline"] = "Not tradable — risk engine blocked"
            result["detail"] = risk.blockers[0]
    return result


def _gap_at_open_pct(quote: dict) -> float | None:
    open_px = quote.get("open")
    prev = quote.get("prev_close")
    if not open_px or not prev or prev <= 0:
        return None
    return ((open_px - prev) / prev) * 100.0


def _pct(from_px: float, to_px: float) -> float:
    if from_px <= 0:
        return 0.0
    return ((to_px - from_px) / from_px) * 100.0


def _trade_plan(
    entry_price: float,
    deploy_dollar: float,
    net_target: float,
) -> dict:
    if entry_price <= 0 or deploy_dollar <= 0:
        return {}
    shares = int((deploy_dollar - DEFAULT_BUY_FEE) / entry_price)
    if shares <= 0:
        return {}
    stop_px = entry_price * (1 - STOP_PCT / 100)
    target_px = round(
        sell_price_for_net_target(
            entry_price=entry_price,
            shares=shares,
            net_target=net_target,
        ),
        2,
    )
    fees = round_trip_fees()
    return {
        "entry_price": round(entry_price, 2),
        "shares": shares,
        "target_price": target_px,
        "stop_price": round(stop_px, 2),
        "target_pct": round(target_move_pct(entry_price, target_px), 2),
        "fees_round_trip": fees,
    }


def assess_entry_tradability(
    *,
    quote: dict | None,
    entry_price: float,
    deploy_dollar: float,
    net_target: float | None = None,
    avg_range_pct: float | None = None,
    dollar_history: DollarHistoryStats | None = None,
    conn: sqlite3.Connection | None = None,
    ticker: str | None = None,
    block_new_longs: bool = False,
) -> dict:
    """Return tradability verdict for entering at ``entry_price`` right now."""
    goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    plan = _trade_plan(entry_price=entry_price, deploy_dollar=deploy_dollar, net_target=goal)
    if not plan or not quote:
        return {
            "verdict": "UNKNOWN",
            "headline": "Cannot assess — missing quote or invalid entry",
            "detail": "Refresh live data and confirm entry price.",
            "checks": [],
            "plan": plan or {},
        }

    price = float(quote.get("price") or entry_price)
    open_px = quote.get("open")
    high = quote.get("high")
    low = quote.get("low")
    target_px = float(plan["target_price"])
    stop_px = float(plan["stop_price"])
    shares = int(plan["shares"])
    target_pct = float(plan["target_pct"])

    checks: list[dict] = []
    blockers: list[str] = []
    cautions: list[str] = []

    def add(name: str, ok: bool | None, message: str) -> None:
        checks.append({"name": name, "ok": ok, "message": message})

    gap_pct = _gap_at_open_pct(quote)
    if gap_pct is not None:
        if gap_pct > MAX_GAP_UP_PCT:
            blockers.append(f"Gap up {gap_pct:.2f}% at open — chasing, little upside room")
            add("Gap at open", False, f"+{gap_pct:.2f}% vs prior close (max {MAX_GAP_UP_PCT}%)")
        elif gap_pct < -MAX_GAP_DOWN_PCT:
            cautions.append(f"Gap down {gap_pct:.2f}% — weak open")
            add("Gap at open", None, f"{gap_pct:.2f}% vs prior close")
        else:
            add("Gap at open", True, f"{gap_pct:+.2f}% vs prior close")

    if open_px and open_px > 0 and entry_price > open_px:
        chase = _pct(open_px, entry_price)
        if chase > MAX_CHASE_ABOVE_OPEN_PCT:
            blockers.append(f"Entry {chase:.2f}% above open — need extra upside for ${goal:.0f}")
            add("Chase above open", False, f"+{chase:.2f}% above today's open")
        elif chase > 0.15:
            cautions.append(f"Buying {chase:.2f}% above open")
            add("Chase above open", None, f"+{chase:.2f}% above open")
        else:
            add("Chase above open", True, f"{chase:+.2f}% vs open")

    remaining_pct = _pct(entry_price, target_px)
    add(
        "Room to target",
        True if remaining_pct >= target_pct * 0.9 else None,
        f"Need +{remaining_pct:.2f}% to ${target_px:.2f} sell ({target_pct:.2f}% move)",
    )

    max_net_at_high: float | None = None
    if high is not None and high > 0:
        max_net_at_high = round(shares * (high - entry_price) - plan["fees_round_trip"], 2)
        required_move = target_px - entry_price
        move_so_far = high - entry_price
        move_ratio = (move_so_far / required_move) if required_move > 0 else 0.0

        if move_ratio >= 0.85 and max_net_at_high < goal * MIN_NET_AT_DAY_HIGH_RATIO:
            blockers.append(
                f"Day high ${high:.2f} only nets ~${max_net_at_high:.0f} from this entry "
                f"(need ${goal:.0f})"
            )
            add(
                "Day-high P&L",
                False,
                f"High ${high:.2f} → ~${max_net_at_high:.0f} net (need ${goal:.0f})",
            )
        elif max_net_at_high >= goal * MIN_NET_AT_DAY_HIGH_RATIO:
            add(
                "Day-high P&L",
                True,
                f"High ${high:.2f} could net ~${max_net_at_high:.0f}",
            )
        else:
            add(
                "Day-high P&L",
                None,
                f"High ${high:.2f} so far — session may still develop (need ${goal:.0f})",
            )

        if high >= target_px:
            if price < target_px * TARGET_RETRACE_TOLERANCE:
                blockers.append(
                    f"Target ${target_px:.2f} already touched — price now ${price:.2f} (missed window)"
                )
                add("Target window", False, f"High reached ${high:.2f}; current ${price:.2f}")
            else:
                add("Target window", True, f"At/above target ${target_px:.2f}")
        else:
            shortfall = target_px - high
            add(
                "Target window",
                None if shortfall / entry_price * 100 < 0.15 else True,
                f"High ${high:.2f} is ${shortfall:.2f} below sell target",
            )

    if low is not None and low <= stop_px:
        blockers.append(f"Session low ${low:.2f} already at/below stop ${stop_px:.2f}")
        add("Stop zone", False, f"Low ${low:.2f} ≤ stop ${stop_px:.2f}")
    else:
        add("Stop zone", True, f"Low ${float(low):.2f} above stop ${stop_px:.2f}" if low is not None else "Low not available")

    if open_px and high is not None and low is not None and open_px > 0:
        session_range = ((high - low) / open_px) * 100.0
        if session_range < MIN_SESSION_RANGE_PCT and remaining_pct > 1.0:
            cautions.append(f"Tight session range {session_range:.2f}% — chop risk")
            add("Session range", None, f"{session_range:.2f}% intraday range (tight)")
        else:
            add("Session range", True, f"{session_range:.2f}% intraday range")

    if avg_range_pct is not None and remaining_pct > avg_range_pct * 0.6:
        cautions.append(
            f"Need +{remaining_pct:.2f}% but typical range ~{avg_range_pct:.1f}%/day"
        )
        add(
            "Vs avg swing",
            None,
            f"Need +{remaining_pct:.2f}% · 20d avg range ~{avg_range_pct:.1f}%",
        )
    elif avg_range_pct is not None:
        add(
            "Vs avg swing",
            True,
            f"Need +{remaining_pct:.2f}% · avg range ~{avg_range_pct:.1f}%",
        )

    dollar_pred = assess_dollar_reachability(
        entry_price=entry_price,
        deploy_dollar=deploy_dollar,
        net_target=goal,
        avg_range_pct=avg_range_pct,
        history=dollar_history,
    )
    for check in dollar_pred.get("checks", []):
        add(check["name"], check["ok"], check["message"])
    if dollar_pred.get("verdict") == "NOT_REACHABLE":
        blockers.append(dollar_pred.get("detail") or "Historical range unlikely to reach $ goal")
    elif dollar_pred.get("verdict") == "MARGINAL":
        cautions.append(dollar_pred.get("detail") or "Marginal historical $ reachability")

    if blockers:
        verdict = "NOT_TRADABLE"
        headline = "Not tradable for today's $ goal"
        detail = blockers[0]
    elif cautions:
        verdict = "CAUTION"
        headline = "Marginal — tight room for $ goal"
        detail = cautions[0]
    else:
        verdict = "TRADABLE"
        headline = "Tradable from this entry"
        detail = f"Room to ${target_px:.2f} sell for ~${goal:.0f} net after fees"

    result = {
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "blockers": blockers,
        "cautions": cautions,
        "gap_at_open_pct": round(gap_pct, 3) if gap_pct is not None else None,
        "remaining_to_target_pct": round(remaining_pct, 3),
        "target_pct_required": target_pct,
        "max_net_at_day_high": max_net_at_high if high is not None else None,
        "net_target": goal,
        "plan": plan,
        "dollar_prediction": dollar_pred,
        "expected_net_at_typical_high": dollar_pred.get("expected_net_at_typical_high"),
        "historical_avg_net_at_high": dollar_pred.get("historical_avg_net_at_high"),
        "dollar_hit_rate_pct": dollar_pred.get("dollar_hit_rate_pct"),
    }
    if conn is not None:
        result = _apply_risk_engine(
            result,
            conn=conn,
            ticker=ticker,
            block_new_longs=block_new_longs,
        )
    return result
