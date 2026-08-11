"""Period screener — aggregate historical Step 3 matches over days/weeks (Phase 7)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.finance import ORIGINAL_BASIS, daily_profit_target
from investment_agent.historical import evaluate_period
from investment_agent.liquidity import MIN_ADV_DOLLAR, SWING_TARGET_PCT
from investment_agent.dollar_target import (
    MIN_RANK_AVG_NET_RATIO,
    MIN_RANK_DOLLAR_DAYS,
    MIN_RANK_DOLLAR_HIT_RATE_PCT,
    passes_dollar_rank_gate,
)
from investment_agent.stock_team import _latest_metrics, screen_candidates
from investment_agent.strategy import REGIME_ONLY_TICKERS

# Rank weights — dollar-goal reachability first (pool is smaller but stronger)
RANK_WEIGHTS = {
    "live_pass": 0.12,
    "dollar_hit_rate": 0.32,
    "dollar_avg_net": 0.22,
    "consistency": 0.10,
    "hit_rate": 0.06,
    "swing_proximity": 0.08,
    "liquidity": 0.06,
    "near_swing": 0.04,
}


def _metrics_map(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {row["ticker"]: row for row in _latest_metrics(conn)}


def _swing_proximity(avg_range_pct: float) -> float:
    return max(0.0, 1.0 - abs(avg_range_pct - SWING_TARGET_PCT) / SWING_TARGET_PCT)


def _liquidity_score(adv_dollar: float, meets_liquidity: bool) -> float:
    if not meets_liquidity or adv_dollar <= 0:
        return 0.0
    return min(1.0, adv_dollar / (MIN_ADV_DOLLAR * 5))


def _criteria_likelihood_score(
    *,
    live_pass: bool,
    hit_rate_pct: float,
    dollar_hit_rate_pct: float = 0.0,
    avg_net_at_high: float = 0.0,
    net_target: float = 150.0,
    days_screened: int,
    avg_range_pct: float,
    adv_dollar: float = 0.0,
    meets_liquidity: bool = False,
    near_swing: bool = False,
    period_days: int = 14,
) -> dict:
    swing_px = _swing_proximity(avg_range_pct)
    liq = _liquidity_score(adv_dollar, meets_liquidity)
    consistency = min(days_screened / max(period_days * 0.5, 1), 1.0)
    hit = hit_rate_pct / 100.0
    dollar_hit = dollar_hit_rate_pct / 100.0
    dollar_avg = (
        min(avg_net_at_high / net_target, 1.0) if net_target > 0 and avg_net_at_high > 0 else 0.0
    )
    score = (
        RANK_WEIGHTS["live_pass"] * (1.0 if live_pass else 0.0)
        + RANK_WEIGHTS["hit_rate"] * hit
        + RANK_WEIGHTS["dollar_hit_rate"] * dollar_hit
        + RANK_WEIGHTS["dollar_avg_net"] * dollar_avg
        + RANK_WEIGHTS["consistency"] * consistency
        + RANK_WEIGHTS["swing_proximity"] * swing_px
        + RANK_WEIGHTS["liquidity"] * liq
        + RANK_WEIGHTS["near_swing"] * (1.0 if near_swing else 0.0)
    )
    return {
        "score": round(score, 4),
        "swing_proximity": round(swing_px, 3),
        "liquidity_score": round(liq, 3),
        "consistency_score": round(consistency, 3),
        "hit_rate_component": round(hit, 3),
        "dollar_hit_rate_component": round(dollar_hit, 3),
        "dollar_avg_net_component": round(dollar_avg, 3),
    }


def _enrich_row(
    row: dict,
    metrics: sqlite3.Row | None,
    *,
    period_days: int,
    net_target: float,
) -> dict:
    adv = float(metrics["adv_dollar"] or 0) if metrics else 0.0
    avg_range = float(row.get("avg_range_pct") or (metrics["avg_range_pct"] if metrics else 0) or 0)
    meets_liq = bool(metrics["meets_liquidity_min"]) if metrics else False
    near_swing = bool(metrics["near_swing_target"]) if metrics else False
    if metrics and avg_range == 0:
        avg_range = float(metrics["avg_range_pct"] or 0)

    parts = _criteria_likelihood_score(
        live_pass=bool(row.get("live_pass_today")),
        hit_rate_pct=float(row.get("hit_rate_pct") or 0),
        dollar_hit_rate_pct=float(row.get("dollar_hit_rate_pct") or 0),
        avg_net_at_high=float(row.get("avg_net_at_high") or 0),
        net_target=net_target,
        days_screened=int(row.get("days_screened") or 0),
        avg_range_pct=avg_range,
        adv_dollar=adv,
        meets_liquidity=meets_liq,
        near_swing=near_swing,
        period_days=period_days,
    )
    out = {**row, **parts}
    out["net_target"] = net_target
    out["passes_dollar_rank_gate"] = passes_dollar_rank_gate(
        dollar_hit_rate_pct=float(row.get("dollar_hit_rate_pct") or 0),
        avg_net_at_high=float(row.get("avg_net_at_high") or 0),
        net_target=net_target,
        days_screened=int(row.get("days_screened") or 0),
    )
    out["avg_range_pct"] = round(avg_range, 2)
    out["adv_dollar"] = round(adv, 0)
    out["adv_dollar_m"] = round(adv / 1_000_000, 1) if adv else 0.0
    out["liquidity_cap"] = round(float(metrics["liquidity_cap"] or 0), 0) if metrics else None
    out["meets_liquidity"] = meets_liq
    out["near_swing_target"] = near_swing
    return out

ET = ZoneInfo("America/New_York")


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


MARKET_CALENDAR_TICKER = "SPY"


def list_trading_dates(
    conn: sqlite3.Connection,
    *,
    count: int,
    end_date: str | None = None,
) -> list[str]:
    """Last ``count`` US market sessions from OHLCV (SPY calendar, excludes weekends/holidays)."""
    end = end_date or _today_et()
    rows = conn.execute(
        """
        SELECT DISTINCT date FROM ohlcv_daily
        WHERE ticker = ? AND date <= ?
        ORDER BY date DESC
        LIMIT ?
        """,
        (MARKET_CALENDAR_TICKER, end, count),
    ).fetchall()
    if len(rows) < count:
        rows = conn.execute(
            """
            SELECT DISTINCT date FROM ohlcv_daily
            WHERE date <= ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (end, count),
        ).fetchall()
    return sorted(row[0] for row in rows)


def date_range_for_period(
    period_days: int,
    end_date: str | None = None,
    *,
    conn: sqlite3.Connection | None = None,
) -> tuple[str, str]:
    """Return [start, end] spanning the last ``period_days`` trading sessions."""
    if conn is not None:
        dates = list_trading_dates(conn, count=period_days, end_date=end_date)
        if dates:
            return dates[0], dates[-1]
    end = end_date or _today_et()
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    # Calendar fallback when no OHLCV (tests): widen window to approximate sessions.
    start_dt = end_dt - timedelta(days=max(int(period_days * 2), period_days))
    return start_dt.strftime("%Y-%m-%d"), end


def _rank_score(
    *,
    live_pass: bool,
    hit_rate_pct: float,
    dollar_hit_rate_pct: float = 0.0,
    avg_net_at_high: float = 0.0,
    net_target: float = 150.0,
    days_screened: int,
    avg_range_pct: float,
    adv_dollar: float = 0.0,
    meets_liquidity: bool = False,
    near_swing: bool = False,
    period_days: int = 14,
) -> float:
    return _criteria_likelihood_score(
        live_pass=live_pass,
        hit_rate_pct=hit_rate_pct,
        dollar_hit_rate_pct=dollar_hit_rate_pct,
        avg_net_at_high=avg_net_at_high,
        net_target=net_target,
        days_screened=days_screened,
        avg_range_pct=avg_range_pct,
        adv_dollar=adv_dollar,
        meets_liquidity=meets_liquidity,
        near_swing=near_swing,
        period_days=period_days,
    )["score"]


def run_period_screener(
    conn: sqlite3.Connection,
    *,
    start_date: str,
    end_date: str,
    tradable_cash: float = ORIGINAL_BASIS,
    min_days_screened: int = 1,
    min_hit_rate_pct: float | None = None,
    min_dollar_hit_rate_pct: float | None = None,
    trading_dates: list[str] | None = None,
    requested_trading_days: int | None = None,
) -> dict:
    """Aggregate period evaluation by ticker and rank candidates."""
    net_target = daily_profit_target(tradable_cash)
    period = evaluate_period(
        conn,
        start_date,
        end_date,
        tradable_cash=tradable_cash,
        trading_dates=trading_dates,
    )
    live_tickers = {c.ticker for c in screen_candidates(conn)}
    metrics_by_ticker = _metrics_map(conn)
    trading_days_in_period = period["days_evaluated"]
    score_period_days = requested_trading_days or trading_days_in_period

    agg: dict[str, dict] = {}
    for day in period["days"]:
        for match in day["matches"]:
            ticker = match["ticker"]
            bucket = agg.setdefault(
                ticker,
                {
                    "ticker": ticker,
                    "days_screened": 0,
                    "simulated_targets": 0,
                    "simulated_stops": 0,
                    "simulated_neither": 0,
                    "dollar_targets": 0,
                    "dollar_stops": 0,
                    "dollar_neither": 0,
                    "last_screened_date": None,
                    "avg_range_pct": 0.0,
                    "_range_sum": 0.0,
                    "_net_at_high_sum": 0.0,
                },
            )
            bucket["days_screened"] += 1
            outcome = match.get("outcome") or "neither"
            dollar_outcome = match.get("dollar_outcome") or "neither"
            if outcome == "target":
                bucket["simulated_targets"] += 1
            elif outcome == "stop":
                bucket["simulated_stops"] += 1
            else:
                bucket["simulated_neither"] += 1
            if dollar_outcome == "target":
                bucket["dollar_targets"] += 1
            elif dollar_outcome == "stop":
                bucket["dollar_stops"] += 1
            else:
                bucket["dollar_neither"] += 1
            bucket["last_screened_date"] = day["date"]
            bucket["_range_sum"] += float(match.get("actual_range_pct") or 0)
            bucket["_net_at_high_sum"] += float(match.get("net_at_high") or 0)

    candidates: list[dict] = []
    for ticker, b in agg.items():
        if b["days_screened"] < min_days_screened:
            continue
        decided = b["simulated_targets"] + b["simulated_stops"]
        hit_rate = round(100.0 * b["simulated_targets"] / max(decided, 1), 1)
        dollar_decided = b["dollar_targets"] + b["dollar_stops"]
        dollar_hit_rate = round(100.0 * b["dollar_targets"] / max(dollar_decided, 1), 1)
        if min_hit_rate_pct is not None and hit_rate < min_hit_rate_pct:
            continue
        if min_dollar_hit_rate_pct is not None and dollar_hit_rate < min_dollar_hit_rate_pct:
            continue
        avg_range = round(b["_range_sum"] / max(b["days_screened"], 1), 2)
        avg_net_at_high = round(b["_net_at_high_sum"] / max(b["days_screened"], 1), 2)
        live_pass = ticker in live_tickers
        m = metrics_by_ticker.get(ticker)
        base = {
            "ticker": ticker,
            "days_screened": b["days_screened"],
            "simulated_targets": b["simulated_targets"],
            "simulated_stops": b["simulated_stops"],
            "simulated_neither": b["simulated_neither"],
            "dollar_targets": b["dollar_targets"],
            "dollar_stops": b["dollar_stops"],
            "dollar_neither": b["dollar_neither"],
            "hit_rate_pct": hit_rate,
            "dollar_hit_rate_pct": dollar_hit_rate,
            "avg_net_at_high": avg_net_at_high,
            "avg_range_pct": avg_range,
            "last_screened_date": b["last_screened_date"],
            "live_pass_today": live_pass,
            "period_trading_days": trading_days_in_period,
            "requested_trading_days": score_period_days,
        }
        row = _enrich_row(base, m, period_days=score_period_days, net_target=net_target)
        candidates.append(row)

    candidates.sort(
        key=lambda r: (-r["score"], -r["days_screened"], -r.get("adv_dollar", 0), r["ticker"])
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "period_days": score_period_days,
        "trading_days_in_period": trading_days_in_period,
        "requested_trading_days": score_period_days,
        "net_target": net_target,
        "deploy": tradable_cash,
        "days_evaluated": period["days_evaluated"],
        "candidates": candidates,
        "summary": {
            **period["summary"],
            "unique_tickers_screened": len(candidates),
        },
    }


def save_screener_run(conn: sqlite3.Connection, result: dict, *, run_type: str = "period") -> int:
    started = _utc_now()
    params = {
        "start_date": result["start_date"],
        "end_date": result["end_date"],
        "run_type": run_type,
    }
    summary_payload = {
        **result.get("summary", {}),
        "candidates": result.get("candidates", []),
    }
    cur = conn.execute(
        """
        INSERT INTO screener_runs (run_type, started_at, finished_at, params_json, summary_json, status)
        VALUES (?, ?, ?, ?, ?, 'completed')
        """,
        (
            run_type,
            started,
            _utc_now(),
            json.dumps(params),
            json.dumps(summary_payload),
        ),
    )
    run_id = int(cur.lastrowid)

    for c in result.get("candidates", []):
        conn.execute(
            """
            INSERT INTO period_screener_hits
              (run_id, ticker, hit_date, predicted_range_pct, actual_range_pct,
               simulated_outcome, would_screen, days_screened, hit_rate_pct, score)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (
                run_id,
                c["ticker"],
                c.get("last_screened_date") or result["end_date"],
                c.get("avg_range_pct"),
                c.get("avg_range_pct"),
                f"targets={c['simulated_targets']},stops={c['simulated_stops']}",
                c["days_screened"],
                c["hit_rate_pct"],
                c["score"],
            ),
        )
    return run_id


def get_latest_screener_run(conn: sqlite3.Connection, run_type: str = "period") -> dict | None:
    row = conn.execute(
        """
        SELECT id, run_type, started_at, finished_at, params_json, summary_json, status
        FROM screener_runs
        WHERE run_type = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (run_type,),
    ).fetchone()
    if not row:
        return None
    summary = json.loads(row["summary_json"])
    candidates = summary.pop("candidates", [])
    params = json.loads(row["params_json"])
    return {
        "id": row["id"],
        "run_type": row["run_type"],
        "started_at": row["started_at"],
        "params": params,
        "summary": summary,
        "candidates": candidates,
        "start_date": params.get("start_date"),
        "end_date": params.get("end_date"),
    }


def build_ranked_candidates(
    conn: sqlite3.Connection,
    *,
    period_days: int = 14,
    min_days_screened: int = 1,
    end_date: str | None = None,
    tradable_cash: float | None = None,
    net_target: float | None = None,
    require_dollar_rank_gate: bool = True,
) -> dict:
    from investment_agent.account import build_dashboard_summary

    summary = build_dashboard_summary(conn)
    deploy = float(tradable_cash if tradable_cash is not None else summary.tradable_cash or ORIGINAL_BASIS)
    goal = float(net_target if net_target is not None else summary.daily_target or daily_profit_target(deploy))

    trading_dates = list_trading_dates(conn, count=period_days, end_date=end_date)
    start, end = date_range_for_period(period_days, end_date=end_date, conn=conn)
    period = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        tradable_cash=deploy,
        min_days_screened=min_days_screened,
        trading_dates=trading_dates or None,
        requested_trading_days=period_days,
    )
    live = screen_candidates(conn)
    live_map = {c.ticker: c for c in live}
    metrics_by_ticker = _metrics_map(conn)
    score_period = period_days

    ranked: list[dict] = []
    excluded: list[dict] = []
    seen: set[str] = set()

    for c in period["candidates"]:
        card = live_map.get(c["ticker"])
        row = _enrich_row(c, metrics_by_ticker.get(c["ticker"]), period_days=score_period, net_target=goal)
        enriched = {
            **row,
            "entry_price": card.entry_price if card else None,
            "target_price": card.target_price if card else None,
            "stop_price": card.stop_price if card else None,
            "suggested_size": card.suggested_size if card else row.get("liquidity_cap"),
            "thesis_summary": card.thesis_summary if card else None,
        }
        if require_dollar_rank_gate and not row.get("passes_dollar_rank_gate"):
            excluded.append(enriched)
        else:
            ranked.append(enriched)
        seen.add(c["ticker"])

    for card in live:
        if card.ticker in seen:
            continue
        m = metrics_by_ticker.get(card.ticker)
        base = {
            "ticker": card.ticker,
            "days_screened": 0,
            "simulated_targets": 0,
            "simulated_stops": 0,
            "simulated_neither": 0,
            "dollar_targets": 0,
            "dollar_stops": 0,
            "dollar_neither": 0,
            "hit_rate_pct": 0.0,
            "dollar_hit_rate_pct": 0.0,
            "avg_net_at_high": 0.0,
            "avg_range_pct": card.avg_range_pct,
            "last_screened_date": None,
            "live_pass_today": True,
            "period_trading_days": period.get("trading_days_in_period", period["days_evaluated"]),
            "requested_trading_days": score_period,
        }
        row = _enrich_row(base, m, period_days=score_period, net_target=goal)
        enriched = {
            **row,
            "entry_price": card.entry_price,
            "target_price": card.target_price,
            "stop_price": card.stop_price,
            "suggested_size": card.suggested_size,
            "thesis_summary": card.thesis_summary,
            "liquidity_cap": card.liquidity_cap,
        }
        if require_dollar_rank_gate and not row.get("passes_dollar_rank_gate"):
            excluded.append(enriched)
        else:
            ranked.append(enriched)

    ranked.sort(
        key=lambda r: (-r["score"], -r["days_screened"], -r.get("adv_dollar", 0), r["ticker"])
    )
    return {
        "period_days": period_days,
        "trading_days_in_period": period.get("trading_days_in_period", period["days_evaluated"]),
        "start_date": start,
        "end_date": end,
        "trading_dates": trading_dates,
        "ranked": ranked,
        "excluded": excluded,
        "excluded_count": len(excluded),
        "live_count": len(live),
        "period_unique": len(period["candidates"]),
        "net_target": goal,
        "deploy": deploy,
        "rank_filters": {
            "min_dollar_hit_rate_pct": MIN_RANK_DOLLAR_HIT_RATE_PCT,
            "min_avg_net_ratio": MIN_RANK_AVG_NET_RATIO,
            "min_dollar_days": MIN_RANK_DOLLAR_DAYS,
            "require_dollar_rank_gate": require_dollar_rank_gate,
        },
        "rank_weights": RANK_WEIGHTS,
    }


def promote_ticker_to_queue(conn: sqlite3.Connection, ticker: str) -> dict:
    """Add a single ticker to queue as watching if not already active."""
    from investment_agent.account import build_dashboard_summary
    from investment_agent.stock_team import _active_queue_tickers, build_analysis_card, _latest_metrics

    summary = build_dashboard_summary(conn)
    if summary.block_new_longs:
        return {"ok": False, "message": "Regime blocks new longs."}

    sym = ticker.upper()
    if sym in REGIME_ONLY_TICKERS:
        return {"ok": False, "message": f"{sym} is regime-only."}

    if sym in _active_queue_tickers(conn):
        return {"ok": False, "message": f"{sym} already in active queue."}

    from investment_agent.journal import journal_cash_balance

    sweeps_row = conn.execute(
        "SELECT COALESCE(SUM(management_amount + tax_amount), 0) AS t FROM sweep_history"
    ).fetchone()
    sweeps = float(sweeps_row["t"]) if sweeps_row else 0.0
    tradable = journal_cash_balance(conn) - sweeps

    row = next((r for r in _latest_metrics(conn) if r["ticker"] == sym), None)
    if row is None:
        return {"ok": False, "message": f"No metrics for {sym} — run ingest first."}

    card = build_analysis_card(row, tradable)
    if card is None:
        return {"ok": False, "message": f"{sym} does not pass Step 3 filters today."}

    now = _utc_now()
    conn.execute(
        """
        INSERT INTO queue_items
          (ticker, state, suggested_size, entry_price, target_price, stop_price,
           avg_range_pct, liquidity_cap, thesis_summary, created_at, updated_at)
        VALUES (?, 'watching', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            card.ticker,
            card.suggested_size,
            card.entry_price,
            card.target_price,
            card.stop_price,
            card.avg_range_pct,
            card.liquidity_cap,
            card.thesis_summary,
            now,
            now,
        ),
    )
    return {"ok": True, "message": f"Added {sym} to queue as watching.", "ticker": sym}
