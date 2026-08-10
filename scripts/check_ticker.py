#!/usr/bin/env python3
"""Report why a ticker is or is not an actionable pick today."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment_agent.account import build_dashboard_summary
from investment_agent.db import connect, get_active_watchlist, init_db
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.step3_status import STEP3_STATUS_LABELS, classify_step3_status
from investment_agent.stock_team import screen_candidates
from investment_agent.strategy import REGIME_ONLY_TICKERS
from investment_agent.trading_day import _latest_quote_rows, resolve_actionable_pick
from investment_agent.watchlist import UNIVERSE_DIR, load_tickers_from_file


def _in_preset(ticker: str) -> list[str]:
    presets: list[str] = []
    for path in UNIVERSE_DIR.glob("*.txt"):
        try:
            if ticker in load_tickers_from_file(path):
                presets.append(path.stem)
        except OSError:
            continue
    return presets


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose ticker eligibility for today's pick")
    parser.add_argument("ticker", help="Symbol e.g. AXON")
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args()
    sym = args.ticker.upper().strip()

    path = init_db(args.db)
    conn = connect(path)
    try:
        active = set(get_active_watchlist(conn))
        metrics = conn.execute(
            """
            SELECT m.*
            FROM ticker_metrics m
            INNER JOIN (
              SELECT ticker, MAX(computed_at) AS max_at FROM ticker_metrics GROUP BY ticker
            ) latest ON m.ticker = latest.ticker AND m.computed_at = latest.max_at
            WHERE m.ticker = ?
            """,
            (sym,),
        ).fetchone()

        step3 = classify_step3_status(
            ticker=sym,
            meets_liquidity=bool(metrics["meets_liquidity_min"]) if metrics else None,
            near_swing=bool(metrics["near_swing_target"]) if metrics else None,
            avg_range_pct=float(metrics["avg_range_pct"]) if metrics and metrics["avg_range_pct"] is not None else None,
            regime_only=sym in REGIME_ONLY_TICKERS,
        )

        live_cards = {c.ticker: c for c in screen_candidates(conn)}
        ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
        rank_row = next((r for r in ranked if r["ticker"] == sym), None)

        summary = build_dashboard_summary(conn)
        net_for_plan = max(summary.daily_target - 0, summary.daily_target)
        quotes = _latest_quote_rows(conn, [sym])
        pick, skipped = resolve_actionable_pick(
            conn,
            quotes=quotes,
            deploy=summary.tradable_cash,
            net_target=net_for_plan,
        )
        skipped_row = next((s for s in skipped if s["ticker"] == sym), None)

        report = {
            "ticker": sym,
            "in_active_watchlist": sym in active,
            "in_universe_files": _in_preset(sym),
            "has_metrics": metrics is not None,
            "step3_status": step3,
            "step3_label": STEP3_STATUS_LABELS.get(step3, step3),
            "live_step3_today": sym in live_cards,
            "in_ranked_list": rank_row is not None,
            "rank_score": rank_row.get("score") if rank_row else None,
            "rank_position": next(
                (i + 1 for i, r in enumerate(ranked) if r["ticker"] == sym),
                None,
            ),
            "live_pass_today_flag": bool(rank_row.get("live_pass_today")) if rank_row else False,
            "is_actionable_top_pick": pick is not None and pick["ticker"] == sym,
            "skipped_as_not_tradable": skipped_row,
            "avg_range_pct": float(metrics["avg_range_pct"]) if metrics and metrics["avg_range_pct"] is not None else None,
            "meets_liquidity_min": bool(metrics["meets_liquidity_min"]) if metrics else None,
            "near_swing_target": bool(metrics["near_swing_target"]) if metrics else None,
        }
        if not report["in_active_watchlist"]:
            report["hint"] = (
                "Not in active watchlist — load a preset that includes this symbol "
                "(AXON is in sp500 only), run ingest, then run period screener."
            )
        elif not report["live_step3_today"]:
            report["hint"] = f"On watchlist but fails Step 3 today: {report['step3_label']}."
        elif skipped_row:
            report["hint"] = skipped_row.get("reason") or "Fails live tradability for today's $ goal."
        elif report["is_actionable_top_pick"]:
            report["hint"] = "This is today's actionable top pick (or would be if ranked first)."
        elif rank_row and not rank_row.get("live_pass_today"):
            report["hint"] = "On ranked list historically but not a live Step 3 passer today."

        print(json.dumps(report, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
