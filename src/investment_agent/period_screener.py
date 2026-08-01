"""Period screener — aggregate historical Step 3 matches over days/weeks (Phase 7)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from investment_agent.finance import ORIGINAL_BASIS
from investment_agent.historical import evaluate_period, evaluate_trading_day
from investment_agent.stock_team import screen_candidates
from investment_agent.strategy import REGIME_ONLY_TICKERS

ET = ZoneInfo("America/New_York")


def _today_et() -> str:
    return datetime.now(ET).strftime("%Y-%m-%d")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def date_range_for_period(period_days: int, end_date: str | None = None) -> tuple[str, str]:
    end = end_date or _today_et()
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=max(period_days - 1, 0))
    return start_dt.strftime("%Y-%m-%d"), end


def _rank_score(
    *,
    live_pass: bool,
    hit_rate_pct: float,
    days_screened: int,
    avg_range_pct: float,
) -> float:
    swing_proximity = max(0.0, 1.0 - abs(avg_range_pct - 3.0) / 3.0)
    return (
        0.4 * (1.0 if live_pass else 0.0)
        + 0.3 * (hit_rate_pct / 100.0)
        + 0.2 * min(days_screened / 10.0, 1.0)
        + 0.1 * swing_proximity
    )


def run_period_screener(
    conn: sqlite3.Connection,
    *,
    start_date: str,
    end_date: str,
    tradable_cash: float = ORIGINAL_BASIS,
    min_days_screened: int = 1,
    min_hit_rate_pct: float | None = None,
) -> dict:
    """Aggregate period evaluation by ticker and rank candidates."""
    period = evaluate_period(conn, start_date, end_date, tradable_cash=tradable_cash)
    live_tickers = {c.ticker for c in screen_candidates(conn)}

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
                    "last_screened_date": None,
                    "avg_range_pct": 0.0,
                    "_range_sum": 0.0,
                },
            )
            bucket["days_screened"] += 1
            outcome = match.get("outcome") or "neither"
            if outcome == "target":
                bucket["simulated_targets"] += 1
            elif outcome == "stop":
                bucket["simulated_stops"] += 1
            else:
                bucket["simulated_neither"] += 1
            bucket["last_screened_date"] = day["date"]
            bucket["_range_sum"] += float(match.get("actual_range_pct") or 0)

    candidates: list[dict] = []
    for ticker, b in agg.items():
        if b["days_screened"] < min_days_screened:
            continue
        decided = b["simulated_targets"] + b["simulated_stops"]
        hit_rate = round(100.0 * b["simulated_targets"] / max(decided, 1), 1)
        if min_hit_rate_pct is not None and hit_rate < min_hit_rate_pct:
            continue
        avg_range = round(b["_range_sum"] / max(b["days_screened"], 1), 2)
        live_pass = ticker in live_tickers
        row = {
            "ticker": ticker,
            "days_screened": b["days_screened"],
            "simulated_targets": b["simulated_targets"],
            "simulated_stops": b["simulated_stops"],
            "simulated_neither": b["simulated_neither"],
            "hit_rate_pct": hit_rate,
            "avg_range_pct": avg_range,
            "last_screened_date": b["last_screened_date"],
            "live_pass_today": live_pass,
            "score": round(
                _rank_score(
                    live_pass=live_pass,
                    hit_rate_pct=hit_rate,
                    days_screened=b["days_screened"],
                    avg_range_pct=avg_range,
                ),
                4,
            ),
        }
        candidates.append(row)

    candidates.sort(key=lambda r: (-r["score"], -r["days_screened"], r["ticker"]))

    return {
        "start_date": start_date,
        "end_date": end_date,
        "period_days": (
            datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
        ).days
        + 1,
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
) -> dict:
    start, end = date_range_for_period(period_days)
    period = run_period_screener(
        conn,
        start_date=start,
        end_date=end,
        min_days_screened=min_days_screened,
    )
    live = screen_candidates(conn)
    live_map = {c.ticker: c for c in live}

    ranked: list[dict] = []
    seen: set[str] = set()

    for c in period["candidates"]:
        card = live_map.get(c["ticker"])
        ranked.append(
            {
                **c,
                "entry_price": card.entry_price if card else None,
                "target_price": card.target_price if card else None,
                "stop_price": card.stop_price if card else None,
                "suggested_size": card.suggested_size if card else None,
                "thesis_summary": card.thesis_summary if card else None,
            }
        )
        seen.add(c["ticker"])

    for card in live:
        if card.ticker in seen:
            continue
        ranked.append(
            {
                "ticker": card.ticker,
                "days_screened": 0,
                "simulated_targets": 0,
                "simulated_stops": 0,
                "simulated_neither": 0,
                "hit_rate_pct": 0.0,
                "avg_range_pct": card.avg_range_pct,
                "last_screened_date": None,
                "live_pass_today": True,
                "score": round(
                    _rank_score(
                        live_pass=True,
                        hit_rate_pct=0.0,
                        days_screened=0,
                        avg_range_pct=card.avg_range_pct,
                    ),
                    4,
                ),
                "entry_price": card.entry_price,
                "target_price": card.target_price,
                "stop_price": card.stop_price,
                "suggested_size": card.suggested_size,
                "thesis_summary": card.thesis_summary,
            }
        )

    ranked.sort(key=lambda r: (-r["score"], -r["days_screened"], r["ticker"]))
    return {
        "period_days": period_days,
        "start_date": start,
        "end_date": end,
        "ranked": ranked,
        "live_count": len(live),
        "period_unique": len(period["candidates"]),
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
