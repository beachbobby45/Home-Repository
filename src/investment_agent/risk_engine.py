"""Independent Risk Engine — approves or rejects trade proposals (Phase 1).

The LLM and strategy layers may recommend trades; this module has final
portfolio and per-trade gate authority before human approval.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from investment_agent.account import cumulative_sweeps, get_setting, set_setting
from investment_agent.finance import DEFAULT_BUY_FEE, ORIGINAL_BASIS, round_trip_fees
from investment_agent.journal import (
    compute_today_realized_net,
    compute_weekly_realized_net,
    count_buys_today,
    get_open_positions,
    journal_cash_balance,
    today_pt_str,
)
from investment_agent.strategy import MAX_TRADES_PER_DAY, STOP_PCT

PT = ZoneInfo("America/Los_Angeles")

# Phase 1 Capital Builder defaults (PHASE1_CAPITAL_BUILDER_SPEC §5.3.2)
RISK_MAX_PCT_PER_TRADE = 1.0
RISK_MIN_PCT_PER_TRADE = 0.5
RISK_MAX_EXPOSURE_PCT = 100.0
RISK_MAX_OPEN_POSITIONS = 2
RISK_DAILY_LOSS_LIMIT_PCT = 2.0
RISK_WEEKLY_LOSS_LIMIT_PCT = 5.0
RISK_MAX_DRAWDOWN_PCT = 10.0
RISK_MIN_RR = 1.5

KILL_SWITCH_KEY = "kill_switch"
PHASE1_HIGH_WATER_KEY = "phase1_high_water_mark"


@dataclass(frozen=True)
class RiskConfig:
    max_pct_per_trade: float = RISK_MAX_PCT_PER_TRADE
    min_pct_per_trade: float = RISK_MIN_PCT_PER_TRADE
    max_exposure_pct: float = RISK_MAX_EXPOSURE_PCT
    max_open_positions: int = RISK_MAX_OPEN_POSITIONS
    daily_loss_limit_pct: float = RISK_DAILY_LOSS_LIMIT_PCT
    weekly_loss_limit_pct: float = RISK_WEEKLY_LOSS_LIMIT_PCT
    max_drawdown_pct: float = RISK_MAX_DRAWDOWN_PCT
    min_reward_risk: float = RISK_MIN_RR
    max_trades_per_day: int = MAX_TRADES_PER_DAY


@dataclass(frozen=True)
class TradeProposalPlan:
    ticker: str
    entry_price: float
    stop_price: float
    target_price: float
    shares: int
    liquidity_cap: float | None = None


@dataclass(frozen=True)
class PortfolioSnapshot:
    tradable_cash: float
    open_positions: list[dict]
    today_realized_net: float
    weekly_realized_net: float
    buys_today: int
    high_water_mark: float
    current_equity: float
    drawdown_pct: float
    kill_switch_active: bool


@dataclass(frozen=True)
class MarketSnapshot:
    block_new_longs: bool
    regime_summary: str | None = None


@dataclass
class RiskDecision:
    verdict: str  # approved | rejected
    headline: str
    checks: list[dict] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    max_risk_dollars: float = 0.0
    recommended_shares: int = 0
    reward_risk_ratio: float | None = None


def is_kill_switch_active(conn: sqlite3.Connection) -> bool:
    return get_setting(conn, KILL_SWITCH_KEY, "0").strip() in ("1", "true", "True", "on", "ON")


def set_kill_switch(conn: sqlite3.Connection, active: bool) -> bool:
    set_setting(conn, KILL_SWITCH_KEY, "1" if active else "0")
    return active


def _read_high_water(conn: sqlite3.Connection) -> float:
    raw = get_setting(conn, PHASE1_HIGH_WATER_KEY, "")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return ORIGINAL_BASIS


def _update_high_water(conn: sqlite3.Connection, equity: float) -> float:
    current_hw = _read_high_water(conn)
    new_hw = max(current_hw, equity)
    if new_hw > current_hw:
        set_setting(conn, PHASE1_HIGH_WATER_KEY, f"{new_hw:.2f}")
    return new_hw


def build_portfolio_snapshot(
    conn: sqlite3.Connection,
    *,
    date_key: str | None = None,
) -> PortfolioSnapshot:
    when = date_key or today_pt_str()
    journal_cash = journal_cash_balance(conn)
    sweeps = cumulative_sweeps(conn)
    tradable = journal_cash - sweeps
    open_positions = get_open_positions(conn)
    open_exposure = sum(p.get("cost_basis", 0) for p in open_positions)
    current_equity = tradable + open_exposure
    high_water = _update_high_water(conn, current_equity)
    drawdown = 0.0
    if high_water > 0:
        drawdown = max(0.0, (high_water - current_equity) / high_water * 100.0)

    return PortfolioSnapshot(
        tradable_cash=round(tradable, 2),
        open_positions=open_positions,
        today_realized_net=round(compute_today_realized_net(conn, when), 2),
        weekly_realized_net=round(compute_weekly_realized_net(conn, when), 2),
        buys_today=count_buys_today(conn, when),
        high_water_mark=round(high_water, 2),
        current_equity=round(current_equity, 2),
        drawdown_pct=round(drawdown, 2),
        kill_switch_active=is_kill_switch_active(conn),
    )


def portfolio_status_dict(snapshot: PortfolioSnapshot, config: RiskConfig | None = None) -> dict:
    cfg = config or RiskConfig()
    tradable = snapshot.tradable_cash
    daily_limit = tradable * cfg.daily_loss_limit_pct / 100.0
    weekly_limit = tradable * cfg.weekly_loss_limit_pct / 100.0
    return {
        "tradable_cash": snapshot.tradable_cash,
        "current_equity": snapshot.current_equity,
        "high_water_mark": snapshot.high_water_mark,
        "drawdown_pct": snapshot.drawdown_pct,
        "today_realized_net": snapshot.today_realized_net,
        "weekly_realized_net": snapshot.weekly_realized_net,
        "daily_loss_limit_dollars": round(daily_limit, 2),
        "weekly_loss_limit_dollars": round(weekly_limit, 2),
        "open_positions_count": len(snapshot.open_positions),
        "buys_today": snapshot.buys_today,
        "kill_switch_active": snapshot.kill_switch_active,
        "limits": {
            "max_open_positions": cfg.max_open_positions,
            "max_trades_per_day": cfg.max_trades_per_day,
            "max_drawdown_pct": cfg.max_drawdown_pct,
            "daily_loss_limit_pct": cfg.daily_loss_limit_pct,
            "weekly_loss_limit_pct": cfg.weekly_loss_limit_pct,
            "max_risk_per_trade_pct": cfg.max_pct_per_trade,
        },
    }


def _per_share_risk(entry: float, stop: float) -> float:
    return max(entry - stop, 0.0)


def _reward_risk_ratio(entry: float, stop: float, target: float) -> float | None:
    risk = _per_share_risk(entry, stop)
    if risk <= 0:
        return None
    return (target - entry) / risk


def _max_shares_for_risk(
    *,
    entry: float,
    stop: float,
    tradable: float,
    max_pct: float,
    liquidity_cap: float | None,
) -> int:
    per_share = _per_share_risk(entry, stop)
    if entry <= 0 or per_share <= 0:
        return 0
    max_risk_dollars = tradable * max_pct / 100.0
    by_risk = int(max_risk_dollars / per_share)
    deploy_cap = liquidity_cap if liquidity_cap and liquidity_cap > 0 else tradable
    by_capital = int((min(deploy_cap, tradable) - DEFAULT_BUY_FEE) / entry)
    return max(0, min(by_risk, by_capital))


def evaluate_proposal(
    *,
    proposal: TradeProposalPlan,
    portfolio: PortfolioSnapshot,
    market: MarketSnapshot,
    config: RiskConfig | None = None,
) -> RiskDecision:
    """Return APPROVE or REJECT with audit checks. LLM cannot override this."""
    cfg = config or RiskConfig()
    checks: list[dict] = []
    blockers: list[str] = []
    cautions: list[str] = []

    def add(name: str, ok: bool | None, message: str, *, blocking: bool = False) -> None:
        checks.append({"name": name, "ok": ok, "message": message, "blocking": blocking})

    tradable = portfolio.tradable_cash
    daily_limit = tradable * cfg.daily_loss_limit_pct / 100.0
    weekly_limit = tradable * cfg.weekly_loss_limit_pct / 100.0

    # Kill switch
    if portfolio.kill_switch_active:
        blockers.append("Kill switch is ON — no new entries until cleared")
        add("Kill switch", False, "Active — all new entries blocked", blocking=True)
    else:
        add("Kill switch", True, "Off")

    # Drawdown halt (auto-engage kill switch messaging)
    if portfolio.drawdown_pct >= cfg.max_drawdown_pct:
        blockers.append(
            f"Drawdown {portfolio.drawdown_pct:.1f}% ≥ {cfg.max_drawdown_pct:.0f}% limit "
            f"(high water ${portfolio.high_water_mark:,.0f})"
        )
        add(
            "Max drawdown",
            False,
            f"{portfolio.drawdown_pct:.1f}% from high water ${portfolio.high_water_mark:,.0f}",
            blocking=True,
        )
    else:
        add(
            "Max drawdown",
            True,
            f"{portfolio.drawdown_pct:.1f}% / {cfg.max_drawdown_pct:.0f}% max",
        )

    # Daily loss limit
    if portfolio.today_realized_net <= -daily_limit:
        blockers.append(
            f"Daily loss ${portfolio.today_realized_net:,.2f} hit "
            f"−${daily_limit:,.0f} limit ({cfg.daily_loss_limit_pct:.1f}%)"
        )
        add(
            "Daily loss limit",
            False,
            f"Today ${portfolio.today_realized_net:,.2f} ≤ −${daily_limit:,.0f}",
            blocking=True,
        )
    else:
        add(
            "Daily loss limit",
            True,
            f"Today ${portfolio.today_realized_net:,.2f} (limit −${daily_limit:,.0f})",
        )

    # Weekly loss limit
    if portfolio.weekly_realized_net <= -weekly_limit:
        blockers.append(
            f"Weekly loss ${portfolio.weekly_realized_net:,.2f} hit "
            f"−${weekly_limit:,.0f} limit ({cfg.weekly_loss_limit_pct:.1f}%)"
        )
        add(
            "Weekly loss limit",
            False,
            f"Week ${portfolio.weekly_realized_net:,.2f} ≤ −${weekly_limit:,.0f}",
            blocking=True,
        )
    else:
        add(
            "Weekly loss limit",
            True,
            f"Week ${portfolio.weekly_realized_net:,.2f} (limit −${weekly_limit:,.0f})",
        )

    # Max open positions (new entry when already at cap)
    at_cap = len(portfolio.open_positions) >= cfg.max_open_positions
    if at_cap:
        blockers.append(
            f"Already {len(portfolio.open_positions)} open position(s) "
            f"(max {cfg.max_open_positions})"
        )
        add(
            "Max open positions",
            False,
            f"{len(portfolio.open_positions)} / {cfg.max_open_positions}",
            blocking=True,
        )
    else:
        add(
            "Max open positions",
            True,
            f"{len(portfolio.open_positions)} / {cfg.max_open_positions}",
        )

    # Max trades per day (count BUY fills today)
    if portfolio.buys_today >= cfg.max_trades_per_day:
        blockers.append(
            f"Max trades per day ({cfg.max_trades_per_day}) reached "
            f"({portfolio.buys_today} buys logged today)"
        )
        add(
            "Max trades today",
            False,
            f"{portfolio.buys_today} / {cfg.max_trades_per_day} buys today",
            blocking=True,
        )
    else:
        add(
            "Max trades today",
            True,
            f"{portfolio.buys_today} / {cfg.max_trades_per_day} buys today",
        )

    # Regime
    if market.block_new_longs:
        blockers.append("Regime blocks new longs — SPY/DIA/QQQ all down intraday")
        add(
            "Regime",
            False,
            market.regime_summary or "Triple index down",
            blocking=True,
        )
    else:
        add("Regime", True, market.regime_summary or "OK for new longs")

    entry = proposal.entry_price
    stop = proposal.stop_price
    target = proposal.target_price
    shares = proposal.shares

    # Mandatory stop
    if stop <= 0 or entry <= 0 or stop >= entry:
        blockers.append("Mandatory stop missing or invalid (must be below entry)")
        add("Mandatory stop", False, f"Stop ${stop:.2f} invalid for entry ${entry:.2f}", blocking=True)
    else:
        add("Mandatory stop", True, f"Stop ${stop:.2f} ({STOP_PCT}% below entry)")

    # Max risk per trade
    per_share_risk = _per_share_risk(entry, stop)
    trade_risk = per_share_risk * shares if shares > 0 else 0.0
    max_risk_dollars = tradable * cfg.max_pct_per_trade / 100.0
    recommended = _max_shares_for_risk(
        entry=entry,
        stop=stop,
        tradable=tradable,
        max_pct=cfg.max_pct_per_trade,
        liquidity_cap=proposal.liquidity_cap,
    )

    if shares > 0 and trade_risk > max_risk_dollars + 0.01:
        blockers.append(
            f"Trade risk ${trade_risk:,.0f} exceeds {cfg.max_pct_per_trade:.1f}% cap "
            f"(${max_risk_dollars:,.0f})"
        )
        add(
            "Max risk per trade",
            False,
            f"${trade_risk:,.0f} > ${max_risk_dollars:,.0f} ({cfg.max_pct_per_trade:.1f}%)",
            blocking=True,
        )
    elif shares > 0 and trade_risk < tradable * cfg.min_pct_per_trade / 100.0:
        cautions.append(
            f"Trade risk ${trade_risk:,.0f} below {cfg.min_pct_per_trade:.1f}% floor — small size"
        )
        add(
            "Max risk per trade",
            None,
            f"${trade_risk:,.0f} (max ${max_risk_dollars:,.0f})",
        )
    else:
        add(
            "Max risk per trade",
            True,
            f"${trade_risk:,.0f} within ${max_risk_dollars:,.0f} ({cfg.max_pct_per_trade:.1f}%)",
        )

    # Min reward:risk (price move; fees make effective RR slightly lower)
    rr = _reward_risk_ratio(entry, stop, target)
    if rr is not None and rr < cfg.min_reward_risk:
        blockers.append(f"Reward:risk {rr:.2f} below minimum {cfg.min_reward_risk:.1f}")
        add(
            "Min R:R",
            False,
            f"{rr:.2f} : 1 (need ≥ {cfg.min_reward_risk:.1f})",
            blocking=True,
        )
    elif rr is not None:
        add("Min R:R", True, f"{rr:.2f} : 1 (min {cfg.min_reward_risk:.1f})")
    else:
        add("Min R:R", False, "Cannot compute — invalid stop", blocking=True)

    # Exposure cap (long only, no margin)
    new_notional = entry * shares if shares > 0 else 0
    open_exposure = sum(p.get("cost_basis", 0) for p in portfolio.open_positions)
    max_exposure = tradable * cfg.max_exposure_pct / 100.0
    if new_notional + open_exposure > max_exposure + 0.01:
        blockers.append(
            f"Portfolio exposure ${open_exposure + new_notional:,.0f} "
            f"exceeds {cfg.max_exposure_pct:.0f}% cap"
        )
        add(
            "Portfolio exposure",
            False,
            f"${open_exposure + new_notional:,.0f} > ${max_exposure:,.0f}",
            blocking=True,
        )
    else:
        add(
            "Portfolio exposure",
            True,
            f"${open_exposure + new_notional:,.0f} / ${max_exposure:,.0f}",
        )

    if blockers:
        verdict = "rejected"
        headline = "Rejected — " + blockers[0][:120]
    else:
        verdict = "approved"
        headline = f"Approved — ${trade_risk:,.0f} max risk within {cfg.max_pct_per_trade:.1f}% cap"

    return RiskDecision(
        verdict=verdict,
        headline=headline,
        checks=checks,
        blockers=blockers,
        cautions=cautions,
        max_risk_dollars=round(max_risk_dollars, 2),
        recommended_shares=recommended,
        reward_risk_ratio=round(rr, 2) if rr is not None else None,
    )


def evaluate_proposal_from_plan_dict(
    *,
    plan: dict,
    ticker: str,
    portfolio: PortfolioSnapshot,
    market: MarketSnapshot,
    config: RiskConfig | None = None,
    liquidity_cap: float | None = None,
) -> RiskDecision:
    """Adapter for pullback / trade plan dicts from trading_day."""
    entry = float(plan.get("limit_buy_price") or plan.get("entry_price") or 0)
    stop = float(plan.get("stop_price") or 0)
    target = float(plan.get("limit_sell_price") or plan.get("target_price") or 0)
    shares = int(plan.get("shares") or plan.get("recommended_shares") or 0)
    proposal = TradeProposalPlan(
        ticker=ticker,
        entry_price=entry,
        stop_price=stop,
        target_price=target,
        shares=shares,
        liquidity_cap=liquidity_cap,
    )
    return evaluate_proposal(
        proposal=proposal,
        portfolio=portfolio,
        market=market,
        config=config,
    )


def portfolio_allows_new_entries(
    conn: sqlite3.Connection,
    *,
    block_new_longs: bool = False,
    regime_summary: str | None = None,
    config: RiskConfig | None = None,
) -> RiskDecision:
    """Portfolio-level gate without a specific proposal (trading day headline)."""
    portfolio = build_portfolio_snapshot(conn)
    market = MarketSnapshot(block_new_longs=block_new_longs, regime_summary=regime_summary)
    dummy = TradeProposalPlan(
        ticker="—",
        entry_price=100.0,
        stop_price=99.0,
        target_price=102.0,
        shares=0,
    )
    decision = evaluate_proposal(
        proposal=dummy,
        portfolio=portfolio,
        market=market,
        config=config,
    )
    # Zero-share proposal skips per-trade sizing blockers; filter those when shares=0
    if dummy.shares == 0:
        trade_specific = {"Max risk per trade", "Min R:R", "Portfolio exposure", "Mandatory stop"}
        decision.checks = [c for c in decision.checks if c["name"] not in trade_specific]
        decision.blockers = [
            b
            for b in decision.blockers
            if not any(
                kw in b.lower()
                for kw in ("trade risk", "reward:risk", "exposure", "mandatory stop", "invalid")
            )
        ]
        if not decision.blockers:
            decision.verdict = "approved"
            decision.headline = "Portfolio risk OK for new entries"
    return decision


def auto_engaged_kill_switch(conn: sqlite3.Connection, snapshot: PortfolioSnapshot) -> bool:
    """Set kill switch when drawdown exceeds limit; return True if newly engaged."""
    if snapshot.drawdown_pct >= RISK_MAX_DRAWDOWN_PCT and not snapshot.kill_switch_active:
        set_kill_switch(conn, True)
        return True
    return False


def risk_decision_to_dict(decision: RiskDecision) -> dict:
    return {
        "verdict": decision.verdict,
        "headline": decision.headline,
        "checks": decision.checks,
        "blockers": decision.blockers,
        "cautions": decision.cautions,
        "max_risk_dollars": decision.max_risk_dollars,
        "recommended_shares": decision.recommended_shares,
        "reward_risk_ratio": decision.reward_risk_ratio,
    }
