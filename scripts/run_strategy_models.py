#!/usr/bin/env python3
"""Compare original, recommended, and daily-$350 strategy models (60d backtest)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import sqlite3

from investment_agent.backtest_strategy import run_strategy_backtest
from investment_agent.db import connect, init_db
from investment_agent.providers.yfinance_bars import REGIME_INDICES, get_intraday_bars
from investment_agent.strategy_models import (
    DAILY_TARGET_MODEL,
    ORIGINAL_MODEL,
    RECOMMENDED_MODEL,
    daily_profit_target,
)
from investment_agent.period_screener import build_ranked_candidates


def _cache_bars(conn, lookback: int = 60) -> dict:
    ranked = build_ranked_candidates(conn, period_days=lookback)
    top = [
        r["ticker"]
        for r in ranked["ranked"]
        if r["ticker"] not in {"SPY", "DIA", "QQQ"}
    ][:20]
    symbols = sorted(set(top) | set(REGIME_INDICES))
    cache: dict = {}
    print(f"Fetching 5m bars for {len(symbols)} symbols…")
    for sym in symbols:
        cache[sym] = get_intraday_bars(sym, lookback_days=lookback, interval="5m")
    return cache


def _print_result(r) -> None:
    print(f"\n{'=' * 60}")
    print(f"MODEL: {r.model_name}")
    for a in r.assumptions:
        print(f"  • {a}")
    print(f"\n  Starting:     ${r.starting_capital:,.2f}")
    print(f"  Ending:       ${r.ending_capital:,.2f}")
    print(f"  Net return:   {r.total_return_pct:+.2f}%")
    print(f"  Trades:       {r.total_trades} ({r.win_rate_pct}% win)")
    print(f"  Fees:         ${r.total_fees:,.2f}")
    print(f"  Max drawdown: {r.max_drawdown_pct:.2f}%")
    if r.total_swept:
        print(f"  Total swept:  ${r.total_swept:,.2f} (mgmt + tax jars)")
    if r.model_name == DAILY_TARGET_MODEL.name:
        print(f"  Avg daily target: ${r.avg_daily_target:,.0f}")
        print(f"  Days hit target:  {r.days_hit_target} / {len([d for d in r.days if d.qualifiers])}")
    if r.months:
        print("  Months:")
        for m in r.months:
            print(
                f"    {m.month}: net ${m.gross_net:+,.2f} | "
                f"swept ${m.total_sweep:,.2f} | balance ${m.balance_after_sweep:,.2f}"
            )


def main() -> None:
    path = init_db()
    conn = connect(path)
    conn.row_factory = sqlite3.Row

    print("=== DAILY TARGET SCALE (theory) ===")
    for bal in (10_000, 15_000, 20_000, 25_000, 50_000):
        print(f"  ${bal:,.0f} balance → ${daily_profit_target(bal):,.0f}/day target")

    cache = _cache_bars(conn)
    models = [ORIGINAL_MODEL, RECOMMENDED_MODEL, DAILY_TARGET_MODEL]
    results = []
    for model in models:
        print(f"\nRunning {model.name}…")
        results.append(run_strategy_backtest(conn, model, lookback_days=60, intraday_cache=cache))

    conn.close()

    out = Path("data/strategy_model_compare.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            [
                {
                    "model": r.model_name,
                    "ending": r.ending_capital,
                    "return_pct": r.total_return_pct,
                    "trades": r.total_trades,
                    "fees": r.total_fees,
                    "swept": r.total_swept,
                    "days_hit_target": r.days_hit_target,
                }
                for r in results
            ],
            indent=2,
        )
    )

    for r in results:
        _print_result(r)

    print(f"\nComparison saved to {out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
