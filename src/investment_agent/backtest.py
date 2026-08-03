"""Intraday backtest — 5-minute bar replay for ranked universe (Gate 1.5)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Literal

from investment_agent.db import connect, get_ohlcv_bars, init_db
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    ORIGINAL_BASIS,
)
from investment_agent.historical import evaluate_trading_day
from investment_agent.period_screener import build_ranked_candidates, date_range_for_period
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy import REGIME_ONLY_TICKERS, STOP_PCT, TARGET_PCT

ExitReason = Literal["target", "stop", "eod"]


@dataclass
class BacktestTrade:
    date: str
    ticker: str
    rank_score: float
    entry_ts: str
    exit_ts: str
    entry_price: float
    exit_price: float
    shares: float
    gross_pnl: float
    fees: float
    net_pnl: float
    exit_reason: ExitReason
    balance_after: float


@dataclass
class BacktestDaySummary:
    date: str
    regime_blocked: bool
    qualifiers: list[str]
    trades: list[BacktestTrade] = field(default_factory=list)
    day_pnl: float = 0.0


@dataclass
class BacktestResult:
    start_date: str
    end_date: str
    starting_capital: float
    ending_capital: float
    total_return_pct: float
    total_trades: int
    wins: int
    losses: int
    win_rate_pct: float
    total_fees: float
    total_net_pnl: float
    max_drawdown_pct: float
    top_tickers: list[str]
    bar_interval: str
    days: list[BacktestDaySummary]
    trades: list[BacktestTrade]
    spy_return_pct: float | None
    assumptions: list[str]
    errors: list[str]


@dataclass
class _OpenPosition:
    ticker: str
    rank_score: float
    entry_ts: str
    entry_price: float
    shares: float
    target: float
    stop: float
    buy_fee: float


def _group_bars_by_date(bars: list[dict]) -> dict[str, list[dict]]:
    by_date: dict[str, list[dict]] = {}
    for bar in bars:
        by_date.setdefault(bar["date"], []).append(bar)
    for day in by_date:
        by_date[day].sort(key=lambda b: b["ts"])
    return by_date


def _regime_blocks(index_bars: dict[str, list[dict]], bar_idx: int) -> bool:
    """True when SPY, DIA, QQQ are all below their session open at bar_idx."""
    opens: dict[str, float] = {}
    for sym in REGIME_INDICES:
        bars = index_bars.get(sym, [])
        if not bars:
            return False
        opens[sym] = float(bars[0]["open"])
    for sym in REGIME_INDICES:
        bars = index_bars.get(sym, [])
        if bar_idx >= len(bars):
            return False
        if float(bars[bar_idx]["close"]) >= opens[sym]:
            return False
    return True


def _bar_exit_price(
    *,
    target: float,
    stop: float,
    bar: dict,
) -> tuple[float | None, ExitReason | None]:
    h, l = float(bar["high"]), float(bar["low"])
    hit_stop = l <= stop
    hit_target = h >= target
    if hit_stop and hit_target:
        return stop, "stop"
    if hit_stop:
        return stop, "stop"
    if hit_target:
        return target, "target"
    return None, None


def _simulate_trading_day(
    *,
    date: str,
    ordered_tickers: list[str],
    rank_by_ticker: dict[str, float],
    liquidity_caps: dict[str, float],
    ticker_bars: dict[str, list[dict]],
    index_bars: dict[str, list[dict]],
    cash: float,
    buy_fee: float,
    sell_fee: float,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
    max_trades: int | None = None,
) -> tuple[list[BacktestTrade], float]:
    """One position at a time; multiple round trips; rotate through ranked qualifiers."""
    master = index_bars.get("SPY") or next(iter(ticker_bars.values()), [])
    if not master:
        return [], cash

    trades: list[BacktestTrade] = []
    position: _OpenPosition | None = None
    n = len(master)
    queue = list(ordered_tickers)

    for i in range(n):
        if position is not None:
            tbars = ticker_bars.get(position.ticker, [])
            if i >= len(tbars):
                continue
            px, reason = _bar_exit_price(
                target=position.target,
                stop=position.stop,
                bar=tbars[i],
            )
            if px is None:
                continue
            exit_ts = tbars[i]["ts"]
            proceeds = position.shares * px - sell_fee
            gross = position.shares * (px - position.entry_price)
            fees = position.buy_fee + sell_fee
            net = gross - fees
            cash += proceeds
            closed_ticker = position.ticker
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=closed_ticker,
                    rank_score=position.rank_score,
                    entry_ts=position.entry_ts,
                    exit_ts=exit_ts,
                    entry_price=round(position.entry_price, 4),
                    exit_price=round(px, 4),
                    shares=position.shares,
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason=reason,
                    balance_after=round(cash, 2),
                )
            )
            position = None
            if max_trades is not None and len(trades) >= max_trades:
                break
            # rotate to back of queue so other ranked names get turns same day
            if closed_ticker in queue:
                queue.remove(closed_ticker)
                queue.append(closed_ticker)
            continue

        if _regime_blocks(index_bars, i):
            continue

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
            cash -= cost
            position = _OpenPosition(
                ticker=ticker,
                rank_score=rank_by_ticker.get(ticker, 0),
                entry_ts=tbars[i]["ts"],
                entry_price=entry_price,
                shares=float(shares),
                target=entry_price * (1 + target_pct / 100),
                stop=entry_price * (1 - stop_pct / 100),
                buy_fee=buy_fee,
            )
            break

    if position is not None:
        tbars = ticker_bars.get(position.ticker, [])
        if tbars:
            last = tbars[-1]
            px = float(last["close"])
            proceeds = position.shares * px - sell_fee
            gross = position.shares * (px - position.entry_price)
            fees = position.buy_fee + sell_fee
            net = gross - fees
            cash += proceeds
            trades.append(
                BacktestTrade(
                    date=date,
                    ticker=position.ticker,
                    rank_score=position.rank_score,
                    entry_ts=position.entry_ts,
                    exit_ts=last["ts"],
                    entry_price=round(position.entry_price, 4),
                    exit_price=round(px, 4),
                    shares=position.shares,
                    gross_pnl=round(gross, 2),
                    fees=fees,
                    net_pnl=round(net, 2),
                    exit_reason="eod",
                    balance_after=round(cash, 2),
                )
            )
    return trades, cash


def _top_ranked_tickers(conn: sqlite3.Connection, *, period_days: int, top_n: int) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=period_days)
    out: list[dict] = []
    for row in ranked["ranked"]:
        if row["ticker"] in REGIME_ONLY_TICKERS:
            continue
        out.append(row)
        if len(out) >= top_n:
            break
    return out


def _qualifiers_for_day(
    conn: sqlite3.Connection,
    eval_date: str,
    tickers: set[str],
    *,
    tradable_cash: float,
) -> dict[str, dict]:
    day = evaluate_trading_day(conn, eval_date, tradable_cash=tradable_cash)
    return {
        m["ticker"]: m
        for m in day["screened_matches"]
        if m["ticker"] in tickers
    }


def _spy_return(conn: sqlite3.Connection, start_date: str, end_date: str) -> float | None:
    bars = get_ohlcv_bars(conn, "SPY", start_date=start_date, end_date=end_date)
    if len(bars) < 2:
        return None
    first = next((b for b in bars if b["date"] >= start_date), bars[0])
    last = next((b for b in reversed(bars) if b["date"] <= end_date), bars[-1])
    o, c = float(first["open"]), float(last["close"])
    if o <= 0:
        return None
    return round((c - o) / o * 100, 2)


def run_intraday_backtest(
    conn: sqlite3.Connection,
    *,
    lookback_days: int = 60,
    top_n: int = 20,
    starting_capital: float = ORIGINAL_BASIS,
    bar_interval: str = "5m",
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    target_pct: float = TARGET_PCT,
    stop_pct: float = STOP_PCT,
    max_trades_per_day: int | None = None,
    intraday_cache: dict[str, list[dict]] | None = None,
) -> BacktestResult:
    start_date, end_date = date_range_for_period(lookback_days)
    top_rows = _top_ranked_tickers(conn, period_days=lookback_days, top_n=top_n)
    top_tickers = {r["ticker"] for r in top_rows}
    rank_by_ticker = {r["ticker"]: float(r.get("score") or 0) for r in top_rows}

    errors: list[str] = []
    cache = intraday_cache if intraday_cache is not None else {}
    symbols = sorted(top_tickers | set(REGIME_INDICES))

    for sym in symbols:
        if sym in cache:
            continue
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
    peak = starting_capital
    max_dd = 0.0

    for date in trading_dates:
        qualifiers = _qualifiers_for_day(conn, date, top_tickers, tradable_cash=cash)
        ordered = sorted(
            qualifiers.keys(),
            key=lambda t: (-rank_by_ticker.get(t, 0), t),
        )

        index_bars = {sym: index_by_date[sym].get(date, []) for sym in REGIME_INDICES}
        regime_blocked = bool(index_bars.get("SPY")) and _regime_blocks(index_bars, 0)

        ticker_bars = {
            t: ticker_by_date[t].get(date, [])
            for t in ordered
            if ticker_by_date.get(t, {}).get(date)
        }
        caps = {t: float(qualifiers[t].get("liquidity_cap") or cash) for t in ordered}

        day_trades: list[BacktestTrade] = []
        if ordered and not regime_blocked:
            day_trades, cash = _simulate_trading_day(
                date=date,
                ordered_tickers=ordered,
                rank_by_ticker=rank_by_ticker,
                liquidity_caps=caps,
                ticker_bars=ticker_bars,
                index_bars=index_bars,
                cash=cash,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
                target_pct=target_pct,
                stop_pct=stop_pct,
                max_trades=max_trades_per_day,
            )
            all_trades.extend(day_trades)

        peak = max(peak, cash)
        dd = (peak - cash) / peak * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)

        day_summaries.append(
            BacktestDaySummary(
                date=date,
                regime_blocked=regime_blocked,
                qualifiers=ordered,
                trades=day_trades,
                day_pnl=round(sum(t.net_pnl for t in day_trades), 2),
            )
        )

    wins = sum(1 for t in all_trades if t.net_pnl > 0)
    losses = sum(1 for t in all_trades if t.net_pnl <= 0)
    total_fees = sum(t.fees for t in all_trades)
    total_net = cash - starting_capital

    return BacktestResult(
        start_date=start_date,
        end_date=end_date,
        starting_capital=starting_capital,
        ending_capital=round(cash, 2),
        total_return_pct=round(total_net / starting_capital * 100, 2),
        total_trades=len(all_trades),
        wins=wins,
        losses=losses,
        win_rate_pct=round(100.0 * wins / max(len(all_trades), 1), 1),
        total_fees=round(total_fees, 2),
        total_net_pnl=round(total_net, 2),
        max_drawdown_pct=round(max_dd, 2),
        top_tickers=[r["ticker"] for r in top_rows],
        bar_interval=bar_interval,
        days=day_summaries,
        trades=all_trades,
        spy_return_pct=_spy_return(conn, start_date, end_date),
        assumptions=[
            f"Top {top_n} tickers by {lookback_days}d rank score; Yahoo {bar_interval} bars (not tick data).",
            f"Entry at {bar_interval} bar open; exit on first touch of +{target_pct}% / −{stop_pct}% (stop wins if both in same bar).",
            "Step 3 qualification from daily bars (liquidity + ~3% swing band) per day.",
            "One position at a time; multiple round trips/day; rotates through ranked qualifiers."
            + (f"; max {max_trades_per_day} trades/day." if max_trades_per_day else "."),
            f"Fees: ${buy_fee:.0f} buy + ${sell_fee:.0f} sell per round trip.",
            "Regime gate: no new entries when SPY/DIA/QQQ all below session open.",
        ],
        errors=errors,
    )


def backtest_to_dict(result: BacktestResult) -> dict:
    return {
        "start_date": result.start_date,
        "end_date": result.end_date,
        "starting_capital": result.starting_capital,
        "ending_capital": result.ending_capital,
        "total_return_pct": result.total_return_pct,
        "total_trades": result.total_trades,
        "wins": result.wins,
        "losses": result.losses,
        "win_rate_pct": result.win_rate_pct,
        "total_fees": result.total_fees,
        "total_net_pnl": result.total_net_pnl,
        "max_drawdown_pct": result.max_drawdown_pct,
        "top_tickers": result.top_tickers,
        "bar_interval": result.bar_interval,
        "spy_return_pct": result.spy_return_pct,
        "assumptions": result.assumptions,
        "errors": result.errors,
        "days": [
            {
                "date": d.date,
                "regime_blocked": d.regime_blocked,
                "qualifiers": d.qualifiers,
                "day_pnl": d.day_pnl,
                "trades": [
                    {
                        "ticker": t.ticker,
                        "rank_score": t.rank_score,
                        "entry_ts": t.entry_ts,
                        "exit_ts": t.exit_ts,
                        "entry_price": t.entry_price,
                        "exit_price": t.exit_price,
                        "shares": t.shares,
                        "net_pnl": t.net_pnl,
                        "exit_reason": t.exit_reason,
                        "balance_after": t.balance_after,
                    }
                    for t in d.trades
                ],
            }
            for d in result.days
        ],
        "trades": [
            {
                "date": t.date,
                "ticker": t.ticker,
                "rank_score": t.rank_score,
                "entry_ts": t.entry_ts,
                "exit_ts": t.exit_ts,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "shares": t.shares,
                "gross_pnl": t.gross_pnl,
                "fees": t.fees,
                "net_pnl": t.net_pnl,
                "exit_reason": t.exit_reason,
                "balance_after": t.balance_after,
            }
            for t in result.trades
        ],
    }


def run_backtest_from_db(db_path=None, **kwargs) -> BacktestResult:
    path = init_db(db_path)
    conn = connect(path)
    conn.row_factory = sqlite3.Row
    try:
        return run_intraday_backtest(conn, **kwargs)
    finally:
        conn.close()
