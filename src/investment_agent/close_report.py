"""Daily Close and Weekly Close — retrospective Growth Plan attribution.

Shows which top-20 ranked tickers would have hit today's dollar goal from:
- **Open entry** (daily bar open)
- **10:00 ET entry** (first 5m bar at/after 30-minute gate)

Compares journal trades, system #1 pick, and best achievable name on the list.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary
from investment_agent.dollar_target import (
    net_at_high_from_open,
    shares_for_deploy,
    simulate_dollar_outcome,
    target_sell_price,
)
from investment_agent.finance import ORIGINAL_BASIS, daily_profit_target
from investment_agent.historical import evaluate_trading_day
from investment_agent.journal import get_completed_round_trips
from investment_agent.period_screener import (
    date_range_for_period,
    run_period_screener,
)
from investment_agent.strategy_models import RECOMMENDED_MODEL

ET = ZoneInfo("America/New_York")
ENTRY_BAR_DELAY = RECOMMENDED_MODEL.entry_bar_delay  # 6 → 10:00 ET on 5m bars
TOP_N = 20


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def price_at_10_et_from_day_bars(day_bars: list[dict]) -> float | None:
    """Return 10:00 ET entry proxy (open of bar index 6 after 9:30 open)."""
    if len(day_bars) <= ENTRY_BAR_DELAY:
        return None
    bar = day_bars[ENTRY_BAR_DELAY]
    open_px = float(bar.get("open") or 0)
    return round(open_px, 4) if open_px > 0 else None


def fetch_price_at_10_et(
    ticker: str,
    report_date: str,
    *,
    intraday_cache: dict[str, Any] | None = None,
) -> float | None:
    """Fetch 5m bars and return 10:00 ET open for ``report_date``."""
    cache = intraday_cache if intraday_cache is not None else {}
    key = f"{ticker}:{report_date}"
    if key in cache:
        return cache[key]

    try:
        from investment_agent.backtest import _group_bars_by_date
        from investment_agent.providers.yfinance_bars import get_intraday_bars

        bars_key = f"_bars:{ticker}"
        if bars_key not in cache:
            cache[bars_key] = get_intraday_bars(ticker, lookback_days=14, interval="5m")
        by_date = _group_bars_by_date(cache[bars_key])
        px = price_at_10_et_from_day_bars(by_date.get(report_date, []))
        cache[key] = px
        return px
    except Exception:
        cache[key] = None
        return None


def save_rank_snapshot(
    conn: sqlite3.Connection,
    snapshot_date: str,
    ranked: list[dict],
    *,
    top_n: int = TOP_N,
) -> None:
    payload = ranked[:top_n]
    conn.execute(
        """
        INSERT INTO rank_snapshots (snapshot_date, created_at, ranked_json, top_n)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(snapshot_date) DO UPDATE SET
          created_at = excluded.created_at,
          ranked_json = excluded.ranked_json,
          top_n = excluded.top_n
        """,
        (snapshot_date, _utc_now(), json.dumps(payload), top_n),
    )


def get_rank_snapshot(conn: sqlite3.Connection, snapshot_date: str) -> list[dict] | None:
    row = conn.execute(
        "SELECT ranked_json FROM rank_snapshots WHERE snapshot_date = ?",
        (snapshot_date,),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["ranked_json"])


def build_ranked_top20_for_date(
    conn: sqlite3.Connection,
    report_date: str,
    *,
    period_days: int = 14,
) -> list[dict]:
    """Reconstruct top-20 rank as of ``report_date`` (no hindsight re-rank)."""
    stored = get_rank_snapshot(conn, report_date)
    if stored:
        return stored[:TOP_N]

    start, end = date_range_for_period(period_days, end_date=report_date)
    period = run_period_screener(conn, start_date=start, end_date=end, min_days_screened=1)
    day_eval = evaluate_trading_day(conn, report_date)
    screened = {m["ticker"]: m for m in day_eval.get("screened_matches") or []}

    candidates: list[dict] = []
    for c in period.get("candidates") or []:
        ticker = c["ticker"]
        row = dict(c)
        row["live_pass_today"] = ticker in screened
        row["rank_date"] = report_date
        candidates.append(row)

    candidates.sort(
        key=lambda r: (-float(r.get("score") or 0), -int(r.get("days_screened") or 0), r["ticker"])
    )
    top = candidates[:TOP_N]

    if not top:
        from investment_agent.db import get_active_watchlist

        fallback: list[dict] = []
        for ticker in get_active_watchlist(conn):
            if _day_bar(conn, ticker, report_date) is None:
                continue
            m = conn.execute(
                """
                SELECT avg_range_pct, meets_liquidity_min, near_swing_target
                FROM ticker_metrics WHERE ticker = ?
                ORDER BY computed_at DESC LIMIT 1
                """,
                (ticker,),
            ).fetchone()
            fallback.append(
                {
                    "ticker": ticker,
                    "score": 0.5,
                    "days_screened": 0,
                    "hit_rate_pct": 0.0,
                    "dollar_hit_rate_pct": 0.0,
                    "live_pass_today": ticker in screened,
                    "avg_range_pct": float(m["avg_range_pct"]) if m and m["avg_range_pct"] else 3.0,
                }
            )
        fallback.sort(key=lambda r: r["ticker"])
        top = fallback[:TOP_N]

    if top:
        save_rank_snapshot(conn, report_date, top)
    return top


def _day_bar(conn: sqlite3.Connection, ticker: str, report_date: str) -> dict | None:
    from investment_agent.db import get_ohlcv_bars

    rows = get_ohlcv_bars(conn, ticker, start_date=report_date, end_date=report_date)
    if not rows:
        return None
    r = rows[0]
    return {
        "open": float(r["open"]),
        "high": float(r["high"]),
        "low": float(r["low"]),
        "close": float(r["close"]),
    }


def _simulate_entry_close(
    *,
    entry_price: float | None,
    day_bar: dict,
    deploy: float,
    net_target: float,
    entry_label: str,
) -> dict:
    if entry_price is None or entry_price <= 0 or not day_bar:
        return {
            "entry_label": entry_label,
            "entry_price": entry_price,
            "available": False,
        }

    open_px = day_bar["open"]
    high = day_bar["high"]
    low = day_bar["low"]
    shares = shares_for_deploy(entry_price, deploy)
    target_px = target_sell_price(
        entry_price=entry_price,
        deploy_dollar=deploy,
        net_target=net_target,
    )
    outcome = simulate_dollar_outcome(
        entry_price,
        high,
        low,
        deploy_dollar=deploy,
        net_target=net_target,
    )
    net_at_high = net_at_high_from_open(entry_price, high, deploy_dollar=deploy)
    hit_goal = net_at_high >= net_target * 0.98

    return {
        "entry_label": entry_label,
        "entry_price": round(entry_price, 2),
        "available": True,
        "shares": shares,
        "target_sell_price": round(target_px, 2) if target_px else None,
        "net_at_high": net_at_high,
        "hit_goal": hit_goal,
        "outcome": outcome,
        "day_high": round(high, 2),
        "day_low": round(low, 2),
    }


def _evaluate_ticker_close_row(
    conn: sqlite3.Connection,
    row: dict,
    report_date: str,
    *,
    deploy: float,
    net_target: float,
    intraday_cache: dict[str, Any] | None = None,
) -> dict | None:
    ticker = row["ticker"]
    bar = _day_bar(conn, ticker, report_date)
    if not bar:
        return None

    entry_open = bar["open"]
    entry_10 = fetch_price_at_10_et(ticker, report_date, intraday_cache=intraday_cache)

    open_sim = _simulate_entry_close(
        entry_price=entry_open,
        day_bar=bar,
        deploy=deploy,
        net_target=net_target,
        entry_label="open",
    )
    sim_10 = _simulate_entry_close(
        entry_price=entry_10,
        day_bar=bar,
        deploy=deploy,
        net_target=net_target,
        entry_label="10:00_et",
    )

    return {
        "rank": None,  # filled by caller
        "ticker": ticker,
        "score": row.get("score"),
        "live_pass_today": bool(row.get("live_pass_today")),
        "dollar_hit_rate_pct": row.get("dollar_hit_rate_pct"),
        "hit_rate_pct": row.get("hit_rate_pct"),
        "avg_range_pct": row.get("avg_range_pct"),
        "day_open": round(bar["open"], 2),
        "day_high": round(bar["high"], 2),
        "day_low": round(bar["low"], 2),
        "day_close": round(bar["close"], 2),
        "open_entry": open_sim,
        "entry_10_et": sim_10,
        "best_net_at_high": max(
            open_sim.get("net_at_high") or 0,
            sim_10.get("net_at_high") or 0,
        ),
        "hit_goal_either": bool(open_sim.get("hit_goal") or sim_10.get("hit_goal")),
    }


def _journal_for_date(conn: sqlite3.Connection, report_date: str) -> dict:
    legs = conn.execute(
        """
        SELECT id, ticker, side, shares, price, fee, executed_at, notes
        FROM trade_journal
        WHERE substr(executed_at, 1, 10) = ?
        ORDER BY executed_at ASC, id ASC
        """,
        (report_date,),
    ).fetchall()
    journal_legs = [
        {
            "id": r["id"],
            "ticker": r["ticker"],
            "side": r["side"],
            "shares": r["shares"],
            "price": r["price"],
            "fee": r["fee"],
            "executed_at": r["executed_at"],
            "notes": r["notes"],
        }
        for r in legs
    ]

    round_trips = []
    for trip in get_completed_round_trips(conn, limit=100):
        sell_day = trip["sell_at"][:10]
        buy_day = trip["buy_at"][:10]
        if sell_day != report_date and buy_day != report_date:
            continue
        round_trips.append(
            {
                "ticker": trip["ticker"],
                "shares": trip["shares"],
                "buy_price": trip["buy_price"],
                "sell_price": trip["sell_price"],
                "buy_at": trip["buy_at"],
                "sell_at": trip["sell_at"],
                "net_pnl": trip["net_pnl"],
                "same_day": trip["same_day"],
            }
        )

    journal_net = round(sum(t["net_pnl"] for t in round_trips if t["sell_at"][:10] == report_date), 2)
    return {
        "legs": journal_legs,
        "round_trips": round_trips,
        "realized_net": journal_net,
        "traded_today": len(journal_legs) > 0,
    }


def _pick_best_hit(rows: list[dict], *, use_10_et: bool) -> dict | None:
    key = "entry_10_et" if use_10_et else "open_entry"
    hits = [r for r in rows if r.get(key, {}).get("hit_goal")]
    if not hits:
        candidates = [r for r in rows if r.get(key, {}).get("available")]
        if not candidates:
            return None
        return max(candidates, key=lambda r: r[key].get("net_at_high") or 0)
    return max(hits, key=lambda r: r[key].get("net_at_high") or 0)


def _summary_for_rows(
    rows: list[dict],
    *,
    net_target: float,
    deploy: float,
    rank1_ticker: str | None,
    journal: dict,
) -> dict:
    rank1_row = next((r for r in rows if r["ticker"] == rank1_ticker), None) if rank1_ticker else None

    best_open = _pick_best_hit(rows, use_10_et=False)
    best_10 = _pick_best_hit(rows, use_10_et=True)

    def _net(row: dict | None, key: str) -> float | None:
        if not row:
            return None
        return row.get(key, {}).get("net_at_high")

    counter_open = _net(best_open, "open_entry")
    counter_10 = _net(best_10, "entry_10_et")

    return {
        "net_target": net_target,
        "deploy": deploy,
        "rank1_ticker": rank1_ticker,
        "rank1_net_at_high_open": _net(rank1_row, "open_entry"),
        "rank1_net_at_high_10et": _net(rank1_row, "entry_10_et"),
        "rank1_hit_open": bool(rank1_row and rank1_row.get("open_entry", {}).get("hit_goal")),
        "rank1_hit_10et": bool(rank1_row and rank1_row.get("entry_10_et", {}).get("hit_goal")),
        "best_hit_ticker_open": best_open["ticker"] if best_open else None,
        "best_hit_ticker_10et": best_10["ticker"] if best_10 else None,
        "best_net_at_high_open": counter_open,
        "best_net_at_high_10et": counter_10,
        "counterfactual_if_best_open": round(deploy + (counter_open or 0), 2) if counter_open else None,
        "counterfactual_if_best_10et": round(deploy + (counter_10 or 0), 2) if counter_10 else None,
        "counterfactual_if_rank1_open": round(deploy + (_net(rank1_row, "open_entry") or 0), 2)
        if rank1_row
        else None,
        "counterfactual_if_rank1_10et": round(deploy + (_net(rank1_row, "entry_10_et") or 0), 2)
        if rank1_row
        else None,
        "journal_realized_net": journal.get("realized_net", 0),
        "journal_traded": journal.get("traded_today", False),
        "tickers_hit_goal_open": sum(1 for r in rows if r.get("open_entry", {}).get("hit_goal")),
        "tickers_hit_goal_10et": sum(1 for r in rows if r.get("entry_10_et", {}).get("hit_goal")),
        "tickers_evaluated": len(rows),
    }


def generate_daily_close_report(
    conn: sqlite3.Connection,
    report_date: str | None = None,
    *,
    fetch_10_et: bool = True,
    intraday_cache: dict[str, Any] | None = None,
) -> dict:
    """Build Daily Close report for ``report_date`` (default: latest stored OHLCV day)."""
    day = report_date or _latest_ohlcv_date(conn) or _today_et()
    summary_acct = build_dashboard_summary(conn)
    deploy = float(summary_acct.tradable_cash or ORIGINAL_BASIS)
    net_target = float(summary_acct.daily_target or daily_profit_target(deploy))

    ranked = build_ranked_top20_for_date(conn, day)
    cache = intraday_cache if intraday_cache is not None else ({} if fetch_10_et else {"_skip": True})

    full_rows: list[dict] = []
    for i, r in enumerate(ranked):
        row = _evaluate_ticker_close_row(
            conn,
            r,
            day,
            deploy=deploy,
            net_target=net_target,
            intraday_cache=cache if not cache.get("_skip") else None,
        )
        if row:
            row["rank"] = i + 1
            full_rows.append(row)

    step3_rows = [r for r in full_rows if r.get("live_pass_today")]

    journal = _journal_for_date(conn, day)
    rank1 = ranked[0]["ticker"] if ranked else None

    highlights: list[str] = []
    if journal["traded_today"]:
        highlights.append(
            f"Journal: ${journal['realized_net']:+.2f} realized on {day}"
            + (f" ({journal['round_trips'][0]['ticker']})" if journal["round_trips"] else "")
        )
    else:
        highlights.append(f"No journal trades logged for {day}.")

    full_summary = _summary_for_rows(
        full_rows, net_target=net_target, deploy=deploy, rank1_ticker=rank1, journal=journal,
    )
    step3_summary = _summary_for_rows(
        step3_rows, net_target=net_target, deploy=deploy, rank1_ticker=rank1, journal=journal,
    )

    if full_summary["best_hit_ticker_open"]:
        highlights.append(
            f"Best on full top 20 (open): {full_summary['best_hit_ticker_open']} "
            f"→ ~${full_summary['best_net_at_high_open']:.0f} net at high "
            f"({'hit' if full_summary['best_net_at_high_open'] and full_summary['best_net_at_high_open'] >= net_target else 'miss'})"
        )
    if rank1:
        highlights.append(
            f"Ranked #1 was {rank1}: "
            f"open ~${full_summary['rank1_net_at_high_open'] or 0:.0f} / "
            f"10:00 ~${full_summary['rank1_net_at_high_10et'] or 0:.0f} net at high "
            f"(goal ${net_target:.0f})"
        )

    return {
        "report_type": "daily",
        "report_date": day,
        "generated_at": _utc_now(),
        "net_target": net_target,
        "deploy": deploy,
        "highlights": highlights,
        "journal": journal,
        "rank1_ticker": rank1,
        "tabs": {
            "step3_pass": {
                "label": "Step 3 pass only",
                "summary": step3_summary,
                "rows": step3_rows,
            },
            "full_top20": {
                "label": "Full top 20",
                "summary": full_summary,
                "rows": full_rows,
            },
        },
        "assumptions": [
            f"Top {TOP_N} ranked as of {day} (frozen snapshot when saved, else reconstructed from {day} screener).",
            "Open entry = daily bar open; 10:00 ET entry = 5m bar index 6 open (30 min after 9:30).",
            f"One trade per day counterfactual; deploy ${deploy:,.0f}; goal ${net_target:.0f} net.",
            "Exit proxy: sell at day high if it reaches Growth Plan target; else stop/neither from daily bar.",
            "Journal compared by trade date (executed_at date prefix).",
        ],
    }


def _latest_ohlcv_date(conn: sqlite3.Connection, before: str | None = None) -> str | None:
    clause = "WHERE date < ?" if before else ""
    params: tuple[Any, ...] = (before,) if before else ()
    row = conn.execute(
        f"SELECT MAX(date) AS d FROM ohlcv_daily {clause}",
        params,
    ).fetchone()
    return row["d"] if row and row["d"] else None


def _trading_days_in_range(conn: sqlite3.Connection, start: str, end: str) -> list[str]:
    rows = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE date >= ? AND date <= ?
        ORDER BY date ASC
        """,
        (start, end),
    ).fetchall()
    return [r["date"] for r in rows]


def generate_weekly_close_report(
    conn: sqlite3.Connection,
    end_date: str | None = None,
    *,
    fetch_10_et: bool = False,
) -> dict:
    """Weekly Close — aggregate daily close for the last 5 trading days in window."""
    end = end_date or _latest_ohlcv_date(conn) or _today_et()
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    start = (end_dt - timedelta(days=7)).strftime("%Y-%m-%d")
    trading_days = _trading_days_in_range(conn, start, end)[-5:]

    daily_reports: list[dict] = []
    cache: dict[str, Any] = {}
    total_journal = 0.0
    total_best_open = 0.0
    total_best_10 = 0.0
    total_rank1_open = 0.0
    rank1_hits_open = 0
    best_hits_open = 0

    for day in trading_days:
        report = generate_daily_close_report(
            conn, day, fetch_10_et=fetch_10_et, intraday_cache=cache,
        )
        fs = report["tabs"]["full_top20"]["summary"]
        total_journal += fs.get("journal_realized_net") or 0
        if fs.get("best_net_at_high_open"):
            total_best_open += fs["best_net_at_high_open"]
        if fs.get("best_net_at_high_10et"):
            total_best_10 += fs["best_net_at_high_10et"]
        if fs.get("rank1_net_at_high_open"):
            total_rank1_open += fs["rank1_net_at_high_open"]
        if fs.get("rank1_hit_open"):
            rank1_hits_open += 1
        if fs.get("best_hit_ticker_open") and fs.get("best_net_at_high_open", 0) >= report["net_target"]:
            best_hits_open += 1

        daily_reports.append(
            {
                "date": day,
                "highlights": report["highlights"][:2],
                "journal_net": fs.get("journal_realized_net"),
                "rank1": fs.get("rank1_ticker"),
                "rank1_hit_open": fs.get("rank1_hit_open"),
                "best_open": fs.get("best_hit_ticker_open"),
                "best_net_open": fs.get("best_net_at_high_open"),
                "net_target": report["net_target"],
            }
        )

    summary_acct = build_dashboard_summary(conn)
    deploy = float(summary_acct.tradable_cash or ORIGINAL_BASIS)

    return {
        "report_type": "weekly",
        "report_date": end,
        "week_start": trading_days[0] if trading_days else start,
        "week_end": end,
        "trading_days": trading_days,
        "generated_at": _utc_now(),
        "net_target_per_day": daily_reports[0]["net_target"] if daily_reports else daily_profit_target(deploy),
        "summary": {
            "days": len(trading_days),
            "journal_total_net": round(total_journal, 2),
            "counterfactual_best_open_total": round(total_best_open, 2),
            "counterfactual_best_10et_total": round(total_best_10, 2),
            "counterfactual_rank1_open_total": round(total_rank1_open, 2),
            "rank1_hit_days_open": rank1_hits_open,
            "best_hit_days_open": best_hits_open,
            "missed_vs_best_open": round(total_best_open - total_journal, 2),
            "missed_vs_rank1_open": round(total_rank1_open - total_journal, 2),
        },
        "daily_reports": daily_reports,
        "assumptions": [
            "Rolling last 5 trading days with OHLCV in 7-calendar-day window ending on report_date.",
            "Weekly totals sum daily counterfactual 'best on list' nets (one pick per day).",
            "10:00 ET entries fetched only when fetch_10_et=True (slower).",
        ],
    }


def save_close_report(conn: sqlite3.Connection, report: dict) -> int:
    cur = conn.execute(
        """
        INSERT INTO close_reports (report_date, report_type, generated_at, payload_json)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(report_date, report_type) DO UPDATE SET
          generated_at = excluded.generated_at,
          payload_json = excluded.payload_json
        """,
        (
            report["report_date"],
            report["report_type"],
            report["generated_at"],
            json.dumps(report),
        ),
    )
    return int(cur.lastrowid)


def get_close_report(
    conn: sqlite3.Connection,
    report_date: str,
    report_type: str = "daily",
) -> dict | None:
    row = conn.execute(
        """
        SELECT payload_json FROM close_reports
        WHERE report_date = ? AND report_type = ?
        """,
        (report_date, report_type),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def get_or_generate_daily_close(
    conn: sqlite3.Connection,
    report_date: str | None = None,
    *,
    regenerate: bool = False,
    fetch_10_et: bool = True,
) -> dict:
    day = report_date or _latest_ohlcv_date(conn) or _today_et()
    if not regenerate:
        cached = get_close_report(conn, day, "daily")
        if cached:
            return cached
    report = generate_daily_close_report(conn, day, fetch_10_et=fetch_10_et)
    save_close_report(conn, report)
    return report


def get_or_generate_weekly_close(
    conn: sqlite3.Connection,
    end_date: str | None = None,
    *,
    regenerate: bool = False,
    fetch_10_et: bool = False,
) -> dict:
    end = end_date or _latest_ohlcv_date(conn) or _today_et()
    if not regenerate:
        cached = get_close_report(conn, end, "weekly")
        if cached:
            return cached
    report = generate_weekly_close_report(conn, end, fetch_10_et=fetch_10_et)
    save_close_report(conn, report)
    return report


def list_close_report_dates(conn: sqlite3.Connection, report_type: str = "daily", limit: int = 30) -> list[str]:
    rows = conn.execute(
        """
        SELECT report_date FROM close_reports
        WHERE report_type = ?
        ORDER BY report_date DESC
        LIMIT ?
        """,
        (report_type, limit),
    ).fetchall()
    return [r["report_date"] for r in rows]
