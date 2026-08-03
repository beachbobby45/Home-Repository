"""Strategy-model backtest with daily dollar targets and month-end sweeps."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from investment_agent.backtest import (
    BacktestDaySummary,
    BacktestTrade,
    BacktestResult,
    _bar_exit_price,
    _group_bars_by_date,
    _qualifiers_for_day,
    _regime_blocks,
    _spy_return,
    _top_ranked_tickers,
)
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    ORIGINAL_BASIS,
    compute_month_end_sweep,
    round_trip_fees,
)
from investment_agent.period_screener import date_range_for_period
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS
from investment_agent.strategy_models import (
    DAILY_TARGET_MODEL,
    RECOMMENDED_MODEL,
    StrategyModel,
    daily_profit_target,
    target_pct_for_dollars,
)


@dataclass
class MonthSummary:
    month: str
    trading_days: int
    gross_net: float
    management_sweep: float
    tax_sweep: float
    total_sweep: float
    balance_after_sweep: float


@dataclass
class StrategyBacktestResult(BacktestResult):
    model_name: str = ""
    months: list[MonthSummary] = field(default_factory=list)
    total_swept: float = 0.0
    avg_daily_target: float = 0.0
    days_hit_target: int = 0


def _simulate_day_with_model(
    *,
    date: str,
    model: StrategyModel,
    ordered_tickers: list[str],
    rank_by_ticker: dict[str, float],
    liquidity_caps: dict[str, float],
    ticker_bars: dict[str, list[dict]],
    index_bars: dict[str, list[dict]],
    cash: float,
    buy_fee: float,
    sell_fee: float,
    daily_target: float | None,
) -> tuple[list[BacktestTrade], float, bool]:
    master = index_bars.get("SPY") or next(iter(ticker_bars.values()), [])
    if not master:
        return [], cash, False

    trades: list[BacktestTrade] = []
    day_net = 0.0
    day_hit_target = False
    n = len(master)
    queue = list(ordered_tickers)
    position = None
    fees_rt = round_trip_fees(buy_fee, sell_fee)

    for i in range(n):
        if daily_target is not None and day_net >= daily_target:
            day_hit_target = True
            break

        if position is not None:
            tbars = ticker_bars.get(position["ticker"], [])
            if i >= len(tbars):
                continue
            px, reason = _bar_exit_price(
                target=position["target"],
                stop=position["stop"],
                bar=tbars[i],
            )
            if px is None:
                continue
            exit_ts = tbars[i]["ts"]
            proceeds = position["shares"] * px - sell_fee
            gross = position["shares"] * (px - position["entry_price"])
            fees = position["buy_fee"] + sell_fee
            net = gross - fees
            cash += proceeds
            day_net += net
            closed = position["ticker"]
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=closed,
                    rank_score=position["rank_score"],
                    entry_ts=position["entry_ts"],
                    exit_ts=exit_ts,
                    entry_price=round(position["entry_price"], 4),
                    exit_price=round(px, 4),
                    shares=position["shares"],
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason=reason,
                    balance_after=round(cash, 2),
                )
            )
            position = None

            if model.stop_day_after_stop and reason == "stop":
                break
            if len(trades) >= model.max_trades_per_day:
                break
            if daily_target is not None and day_net >= daily_target:
                day_hit_target = True
                break
            if closed in queue:
                queue.remove(closed)
                queue.append(closed)
            continue

        if i < model.entry_bar_delay:
            continue
        if _regime_blocks(index_bars, i):
            continue
        if len(trades) >= model.max_trades_per_day:
            break

        for ticker in queue:
            tbars = ticker_bars.get(ticker, [])
            if i >= len(tbars):
                continue
            entry_price = float(tbars[i]["open"])
            if entry_price <= 0:
                continue
            cap = liquidity_caps.get(ticker, cash)
            deploy = min(cap, cash - buy_fee)
            if deploy <= 0:
                continue
            shares = int(deploy / entry_price)
            if shares <= 0:
                continue
            cost = shares * entry_price + buy_fee
            if cost > cash:
                continue

            if model.target_pct is not None:
                tgt_pct = model.target_pct
            else:
                remaining = (daily_target or 0) - day_net
                if remaining <= 0:
                    day_hit_target = True
                    break
                pct = target_pct_for_dollars(
                    net_needed=remaining,
                    deploy_dollar=shares * entry_price,
                    fees=fees_rt,
                    min_pct=model.min_dynamic_target_pct,
                    max_pct=model.max_dynamic_target_pct,
                )
                if pct is None:
                    continue
                tgt_pct = pct

            cash -= cost
            position = {
                "ticker": ticker,
                "rank_score": rank_by_ticker.get(ticker, 0),
                "entry_ts": tbars[i]["ts"],
                "entry_price": entry_price,
                "shares": float(shares),
                "target": entry_price * (1 + tgt_pct / 100),
                "stop": entry_price * (1 - model.stop_pct / 100),
                "buy_fee": buy_fee,
            }
            break

    if position is not None:
        tbars = ticker_bars.get(position["ticker"], [])
        if tbars:
            last = tbars[-1]
            px = float(last["close"])
            proceeds = position["shares"] * px - sell_fee
            gross = position["shares"] * (px - position["entry_price"])
            fees = position["buy_fee"] + sell_fee
            net = gross - fees
            cash += proceeds
            day_net += net
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=position["ticker"],
                    rank_score=position["rank_score"],
                    entry_ts=position["entry_ts"],
                    exit_ts=last["ts"],
                    entry_price=round(position["entry_price"], 4),
                    exit_price=round(px, 4),
                    shares=position["shares"],
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason="eod",
                    balance_after=round(cash, 2),
                )
            )

    if daily_target is not None and day_net >= daily_target:
        day_hit_target = True
    return trades, cash, day_hit_target


def run_strategy_backtest(
    conn: sqlite3.Connection,
    model: StrategyModel,
    *,
    lookback_days: int = 60,
    top_n: int = 20,
    starting_capital: float = ORIGINAL_BASIS,
    bar_interval: str = "5m",
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    intraday_cache: dict[str, list[dict]] | None = None,
) -> StrategyBacktestResult:
    start_date, end_date = date_range_for_period(lookback_days)
    top_rows = _top_ranked_tickers(conn, period_days=lookback_days, top_n=top_n)
    top_tickers = {r["ticker"] for r in top_rows}
    rank_by_ticker = {r["ticker"]: float(r.get("score") or 0) for r in top_rows}

    errors: list[str] = []
    cache = dict(intraday_cache or {})
    for sym in sorted(top_tickers | set(REGIME_INDICES)):
        if sym not in cache:
            try:
                cache[sym] = get_intraday_bars(sym, lookback_days=lookback_days, interval=bar_interval)
            except Exception as exc:
                errors.append(f"{sym}: {exc}")
                cache[sym] = []

    ticker_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in top_tickers}
    index_by_date = {sym: _group_bars_by_date(cache.get(sym, [])) for sym in REGIME_INDICES}

    trading_dates = sorted(
        {
            d
            for sym in top_tickers
            for d in ticker_by_date.get(sym, {})
            if start_date <= d <= end_date
        }
    )

    cash = starting_capital
    all_trades: list[BacktestTrade] = []
    day_summaries: list[BacktestDaySummary] = []
    month_summaries: list[MonthSummary] = []
    month_net: dict[str, float] = {}
    total_swept = 0.0
    daily_targets_used: list[float] = []
    days_hit_target = 0
    peak = starting_capital
    max_dd = 0.0

    for idx, date in enumerate(trading_dates):
        month_key = date[:7]
        month_net.setdefault(month_key, 0.0)

        day_start_cash = cash
        daily_target = None
        if model.target_pct is None:
            daily_target = daily_profit_target(
                day_start_cash,
                base=model.daily_base_target,
                step=model.daily_step,
                every=model.daily_step_every,
            )
            daily_targets_used.append(daily_target)

        qualifiers = _qualifiers_for_day(conn, date, top_tickers, tradable_cash=cash)
        ordered = sorted(qualifiers.keys(), key=lambda t: (-rank_by_ticker.get(t, 0), t))
        index_bars = {sym: index_by_date[sym].get(date, []) for sym in REGIME_INDICES}
        regime_blocked = bool(index_bars.get("SPY")) and _regime_blocks(index_bars, 0)

        day_trades: list[BacktestTrade] = []
        hit = False
        if ordered and not regime_blocked:
            ticker_bars = {
                t: ticker_by_date[t].get(date, [])
                for t in ordered
                if ticker_by_date.get(t, {}).get(date)
            }
            caps = {t: float(qualifiers[t].get("liquidity_cap") or cash) for t in ordered}
            day_trades, cash, hit = _simulate_day_with_model(
                date=date,
                model=model,
                ordered_tickers=ordered,
                rank_by_ticker=rank_by_ticker,
                liquidity_caps=caps,
                ticker_bars=ticker_bars,
                index_bars=index_bars,
                cash=cash,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
                daily_target=daily_target,
            )
            all_trades.extend(day_trades)
            if hit:
                days_hit_target += 1

        day_pnl = sum(t.net_pnl for t in day_trades)
        month_net[month_key] += day_pnl

        peak = max(peak, cash)
        max_dd = max(max_dd, (peak - cash) / peak * 100 if peak > 0 else 0)

        day_summaries.append(
            BacktestDaySummary(
                date=date,
                regime_blocked=regime_blocked,
                qualifiers=ordered,
                trades=day_trades,
                day_pnl=round(day_pnl, 2),
            )
        )

        next_month = trading_dates[idx + 1][:7] if idx + 1 < len(trading_dates) else None
        if model.apply_monthly_sweeps and (next_month is None or next_month != month_key):
            sweep = compute_month_end_sweep(month_net[month_key])
            if sweep.applies:
                cash -= sweep.total_sweep
                total_swept += sweep.total_sweep
            month_summaries.append(
                MonthSummary(
                    month=month_key,
                    trading_days=sum(1 for d in day_summaries if d.date.startswith(month_key)),
                    gross_net=round(month_net[month_key], 2),
                    management_sweep=round(sweep.management_sweep, 2),
                    tax_sweep=round(sweep.tax_sweep, 2),
                    total_sweep=round(sweep.total_sweep, 2),
                    balance_after_sweep=round(cash, 2),
                )
            )

    wins = sum(1 for t in all_trades if t.net_pnl > 0)
    total_fees = sum(t.fees for t in all_trades)
    total_net = cash - starting_capital

    assumptions = [
        f"Model: {model.name} — {model.description}",
        f"Top {top_n} ranked tickers; Yahoo {bar_interval} bars.",
        f"Stop −{model.stop_pct}%; max {model.max_trades_per_day} trades/day; "
        f"entry after {model.entry_bar_delay * 5} min; "
        + ("stop day after stop-out." if model.stop_day_after_stop else "re-entry allowed."),
    ]
    if model.target_pct is not None:
        assumptions.append(f"Fixed target +{model.target_pct}%.")
    else:
        assumptions.append(
            f"Daily net target ${model.daily_base_target} + ${model.daily_step} per ${model.daily_step_every:,.0f} "
            f"above ${ORIGINAL_BASIS:,.0f}; dynamic per-trade target {model.min_dynamic_target_pct}–"
            f"{model.max_dynamic_target_pct}%."
        )
    if model.apply_monthly_sweeps:
        assumptions.append("Month-end: 10% management + 25% tax on positive monthly net, removed from tradable balance.")
    assumptions.append(f"Fees: ${buy_fee:.0f} buy + ${sell_fee:.0f} sell per round trip.")

    return StrategyBacktestResult(
        start_date=start_date,
        end_date=end_date,
        starting_capital=starting_capital,
        ending_capital=round(cash, 2),
        total_return_pct=round(total_net / starting_capital * 100, 2),
        total_trades=len(all_trades),
        wins=wins,
        losses=len(all_trades) - wins,
        win_rate_pct=round(100.0 * wins / max(len(all_trades), 1), 1),
        total_fees=round(total_fees, 2),
        total_net_pnl=round(total_net, 2),
        max_drawdown_pct=round(max_dd, 2),
        top_tickers=[r["ticker"] for r in top_rows],
        bar_interval=bar_interval,
        days=day_summaries,
        trades=all_trades,
        spy_return_pct=_spy_return(conn, start_date, end_date),
        assumptions=assumptions,
        errors=errors,
        model_name=model.name,
        months=month_summaries,
        total_swept=round(total_swept, 2),
        avg_daily_target=round(sum(daily_targets_used) / max(len(daily_targets_used), 1), 2),
        days_hit_target=days_hit_target,
    )
