"""Intraday trading day status — go/no-go gate, top pick, live refresh."""

from __future__ import annotations

import sqlite3
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from investment_agent.account import build_dashboard_summary, get_setting, set_setting
from investment_agent.finance import (
    DEFAULT_BUY_FEE,
    DEFAULT_SELL_FEE,
    daily_profit_target,
    round_trip_fees,
    sell_price_for_net_target,
    target_move_pct,
)
from investment_agent.journal import (
    compute_today_realized_net,
    get_completed_round_trips,
    get_open_positions,
)
from investment_agent.period_screener import build_ranked_candidates
from investment_agent.regime import REGIME_SYMBOLS
from investment_agent.strategy import ENTRY_DELAY_MINUTES, ENTRY_WINDOW_ET, STOP_PCT
from investment_agent.dollar_target import load_dollar_history
from investment_agent.pullback_entry import (
    LIMIT_FILL_DEADLINE,
    compute_pullback_trade_plan,
    dollar_confidence,
    limit_fill_missed,
)
from investment_agent.tradability import assess_entry_tradability

ET = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
ENTRY_READY = time(10, 0)  # 30 min after open
ENTRY_CUTOFF = time(14, 30)
MARKET_CLOSE = time(16, 0)
QUOTE_STALE_MINUTES = 20
TOP_PICK_MAX_DROP_PCT = 0.50  # down more than 0.5% from open → caution
TOP_PICK_NO_GO_DROP_PCT = 0.75  # aligns with stop width
ACTIONABLE_PICK_SCAN = 10  # walk top N live ranked for tradability


def _session_open_from_quote(quote: dict | None, fallback: float | None = None) -> float | None:
    if not quote:
        return fallback
    open_px = quote.get("open")
    if open_px and open_px > 0:
        return float(open_px)
    return fallback


def _pullback_plan_for_row(
    row: dict,
    quote: dict | None,
    *,
    deploy: float,
    net_target: float,
) -> dict:
    avg_range = float(row.get("avg_range_pct") or 0)
    session_open = _session_open_from_quote(
        quote,
        fallback=float(row.get("entry_price") or row.get("last_quote") or 0) or None,
    )
    if not session_open or session_open <= 0:
        return {}
    return compute_pullback_trade_plan(
        session_open=session_open,
        avg_range_pct=avg_range,
        deploy_dollar=deploy,
        net_target=net_target,
    )


def _assess_pick_tradability(
    row: dict,
    quote: dict | None,
    *,
    deploy: float,
    net_target: float,
    conn: sqlite3.Connection,
) -> tuple[dict, dict, dict]:
    """Return (pullback_plan, tradability, dollar_history dict)."""
    avg_range = float(row.get("avg_range_pct") or 0) or None
    plan = _pullback_plan_for_row(row, quote, deploy=deploy, net_target=net_target)
    limit_entry = plan.get("limit_buy_price") or plan.get("entry_price")
    hist = load_dollar_history(
        conn,
        row["ticker"],
        end_date=today_et_str(),
        deploy_dollar=deploy,
        net_target=net_target,
        avg_range_pct=avg_range,
    )
    tradability = assess_entry_tradability(
        quote=quote,
        entry_price=limit_entry or float(row.get("last_quote") or 0),
        deploy_dollar=deploy,
        net_target=net_target,
        avg_range_pct=avg_range,
        dollar_history=hist,
    ) if limit_entry and quote else {
        "verdict": "UNKNOWN",
        "headline": "No live quote",
        "detail": "Refresh live data for tradability check",
        "checks": [],
    }
    return plan, tradability, hist.to_dict()


def now_et() -> datetime:
    return datetime.now(ET)


def today_et_str() -> str:
    return now_et().strftime("%Y-%m-%d")


def session_phase(when: datetime | None = None) -> str:
    now = when or now_et()
    if now.weekday() >= 5:
        return "weekend"
    t = now.time()
    if t < MARKET_OPEN:
        return "pre_market"
    if t < ENTRY_READY:
        return "opening_wait"
    if t < ENTRY_CUTOFF:
        return "trade_window"
    if t < MARKET_CLOSE:
        return "late_day"
    return "after_hours"


def _latest_quote_rows(conn: sqlite3.Connection, tickers: list[str]) -> dict[str, dict]:
    if not tickers:
        return {}
    placeholders = ",".join("?" for _ in tickers)
    rows = conn.execute(
        f"""
        SELECT q.ticker, q.price, q.open, q.high, q.low, q.prev_close, q.captured_at
        FROM quotes q
        INNER JOIN (
          SELECT ticker, MAX(captured_at) AS max_at
          FROM quotes
          WHERE ticker IN ({placeholders})
          GROUP BY ticker
        ) latest ON q.ticker = latest.ticker AND q.captured_at = latest.max_at
        """,
        tickers,
    ).fetchall()
    return {
        row["ticker"]: {
            "price": float(row["price"]),
            "open": float(row["open"]) if row["open"] else None,
            "high": float(row["high"]) if row["high"] else None,
            "low": float(row["low"]) if row["low"] else None,
            "prev_close": float(row["prev_close"]) if row["prev_close"] else None,
            "captured_at": row["captured_at"],
        }
        for row in rows
    }


def _quote_age_minutes(captured_at: str | None) -> float | None:
    if not captured_at:
        return None
    try:
        ts = captured_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return age.total_seconds() / 60.0
    except ValueError:
        return None


def _intraday_change_pct(quote: dict) -> float | None:
    price = quote.get("price")
    open_px = quote.get("open")
    prev = quote.get("prev_close")
    if price is None:
        return None
    if open_px and open_px > 0:
        return ((price - open_px) / open_px) * 100.0
    if prev and prev > 0:
        return ((price - prev) / prev) * 100.0
    return None


def _opening_range_pct(quote: dict) -> float | None:
    """Approximate session range vs open using quote high/low."""
    open_px = quote.get("open")
    high = quote.get("high")
    low = quote.get("low")
    if not open_px or open_px <= 0 or high is None or low is None:
        return None
    return ((high - low) / open_px) * 100.0


def get_top_pick(conn: sqlite3.Connection) -> dict | None:
    """Highest ranked live candidate that passes the dollar-goal rank gate."""
    pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [
        r for r in ranked
        if r.get("live_pass_today") and r.get("passes_dollar_rank_gate", True)
    ]

    if pinned:
        match = next((r for r in live if r["ticker"] == pinned), None)
        if match:
            return {**match, "source": "pinned"}
        row = next((r for r in ranked if r["ticker"] == pinned), None)
        if row:
            return {**row, "source": "pinned_not_live", "live_pass_today": False}

    if not live:
        return None
    return {**live[0], "source": "ranked_#1"}


def _live_ranked_candidates(conn: sqlite3.Connection, limit: int = ACTIONABLE_PICK_SCAN) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [
        r for r in ranked
        if r.get("live_pass_today") and r.get("passes_dollar_rank_gate", True)
    ]
    pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
    if pinned:
        pin_row = next((r for r in ranked if r["ticker"] == pinned), None)
        if pin_row:
            live = [pin_row] + [r for r in live if r["ticker"] != pinned]
    return live[:limit]


def resolve_actionable_pick(
    conn: sqlite3.Connection,
    *,
    quotes: dict[str, dict],
    deploy: float,
    net_target: float,
) -> tuple[dict | None, list[dict]]:
    """Pick first live ranked name that passes intraday tradability for today's $ goal."""
    skipped: list[dict] = []
    candidates = _live_ranked_candidates(conn)

    for row in candidates:
        sym = row["ticker"]
        quote = quotes.get(sym)
        if not quote or not quote.get("price"):
            skipped.append({
                "ticker": sym,
                "rank_score": row.get("score"),
                "reason": "No live quote",
                "verdict": "UNKNOWN",
            })
            continue

        plan, tradability, hist_dict = _assess_pick_tradability(
            row, quote, deploy=deploy, net_target=net_target, conn=conn
        )
        pick = {
            **row,
            **plan,
            "tradability": tradability,
            "dollar_history": hist_dict,
            "dollar_confidence": dollar_confidence(float(row.get("dollar_hit_rate_pct") or 0)),
        }
        if row.get("source") != "pinned" and sym == get_setting(conn, "pinned_pick_ticker", "").strip().upper():
            pick["source"] = "pinned"

        verdict = tradability.get("verdict")
        if verdict in ("NOT_TRADABLE", "CAUTION"):
            skipped.append({
                "ticker": sym,
                "rank_score": row.get("score"),
                "reason": tradability.get("detail"),
                "verdict": verdict,
                "dollar_hit_rate_pct": row.get("dollar_hit_rate_pct"),
                "expected_net_at_typical_high": tradability.get("expected_net_at_typical_high"),
                "limit_buy_price": plan.get("limit_buy_price"),
            })
            continue

        source = pick.get("source")
        if not source:
            pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
            source = "pinned" if sym == pinned else f"ranked_#{len(skipped) + 1}"
        pick["source"] = source
        return pick, skipped

    return None, skipped


def stopped_out_today(conn: sqlite3.Connection, date_key: str | None = None) -> bool:
    """True if any closed round trip today lost money (stop-out day)."""
    day = date_key or today_et_str()
    for trip in get_completed_round_trips(conn, limit=200):
        sell_day = trip["sell_at"][:10]
        try:
            dt = datetime.fromisoformat(trip["sell_at"].replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            sell_day = dt.astimezone(ET).strftime("%Y-%m-%d")
        except ValueError:
            pass
        if sell_day != day:
            continue
        if trip["net_pnl"] < -20:
            return True
    return False


def refresh_live_quotes(conn: sqlite3.Connection, settings) -> dict:
    """Fetch fresh Finnhub quotes for regime indices, top pick, queue, and open positions."""
    from investment_agent.db import insert_quote, insert_regime_snapshot, log_ingest
    from investment_agent.providers.finnhub import FinnhubClient, utc_now_iso as fh_now
    from investment_agent.regime import evaluate_regime, index_quote_from_finnhub

    symbols: set[str] = set(REGIME_SYMBOLS)
    for row in _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN):
        symbols.add(row["ticker"])

    pick = get_top_pick(conn)
    if pick:
        symbols.add(pick["ticker"])

    rows = conn.execute(
        "SELECT DISTINCT ticker FROM queue_items WHERE state NOT IN ('closed')"
    ).fetchall()
    symbols.update(row["ticker"] for row in rows)
    for pos in get_open_positions(conn):
        symbols.add(pos["ticker"])

    errors: list[str] = []
    updated: list[str] = []
    index_quotes = {}

    if not settings.finnhub_api_key:
        return {
            "ok": False,
            "error": "FINNHUB_API_KEY not set — add to .env to refresh live quotes",
            "symbols_requested": sorted(symbols),
        }

    fh = FinnhubClient(settings.finnhub_api_key)
    try:
        for symbol in sorted(symbols):
            try:
                q = fh.get_quote(symbol)
                insert_quote(
                    conn,
                    {
                        "ticker": symbol,
                        "captured_at": fh_now(),
                        "price": float(q["c"]),
                        "open": float(q.get("o") or 0) or None,
                        "high": float(q.get("h") or 0) or None,
                        "low": float(q.get("l") or 0) or None,
                        "prev_close": float(q.get("pc") or 0) or None,
                    },
                )
                updated.append(symbol)
                if symbol in REGIME_SYMBOLS:
                    index_quotes[symbol] = index_quote_from_finnhub(symbol, q)
            except Exception as exc:
                errors.append(f"{symbol}: {exc}")
                log_ingest(conn, "finnhub", "error", f"refresh {symbol}: {exc}")

        if len(index_quotes) == len(REGIME_SYMBOLS):
            snap = evaluate_regime(index_quotes, fh_now())
            insert_regime_snapshot(
                conn,
                {
                    "captured_at": snap.captured_at,
                    "spy_change_pct": snap.spy_change_pct,
                    "dia_change_pct": snap.dia_change_pct,
                    "qqq_change_pct": snap.qqq_change_pct,
                    "all_indices_down": snap.all_indices_down,
                    "block_new_longs": snap.block_new_longs,
                    "summary": snap.summary,
                },
            )
    finally:
        fh.close()

    return {
        "ok": len(updated) > 0,
        "updated": updated,
        "errors": errors,
        "symbols_requested": sorted(symbols),
    }


TOP_PICK_NO_GO_DROP_PCT = 0.75  # aligns with stop width
MAX_ENTRY_SLIPPAGE_PCT = 0.35  # planned buy vs live — warn above this


def compute_trade_plan(
    *,
    entry_price: float,
    deploy_dollar: float,
    buy_fee: float = DEFAULT_BUY_FEE,
    sell_fee: float = DEFAULT_SELL_FEE,
    net_target: float | None = None,
    stop_pct: float = STOP_PCT,
) -> dict:
    """Shares, Growth-Plan sell price, stop price, and net P&L at each exit."""
    if entry_price <= 0 or deploy_dollar <= 0:
        return {}
    shares = int((deploy_dollar - buy_fee) / entry_price)
    if shares <= 0:
        return {}
    daily_goal = net_target if net_target is not None else daily_profit_target(deploy_dollar)
    stop_px = entry_price * (1 - stop_pct / 100)
    target_px = sell_price_for_net_target(
        entry_price=entry_price,
        shares=shares,
        net_target=daily_goal,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
    )
    target_px = round(target_px, 2)
    notional = shares * entry_price
    total_cost = notional + buy_fee
    net_at_target = round(shares * (target_px - entry_price) - buy_fee - sell_fee, 2)
    net_at_stop = round(shares * (stop_px - entry_price) - buy_fee - sell_fee, 2)
    return {
        "entry_price": round(entry_price, 2),
        "shares": shares,
        "notional": round(notional, 2),
        "total_cost": round(total_cost, 2),
        "target_price": target_px,
        "stop_price": round(stop_px, 2),
        "target_pct": round(target_move_pct(entry_price, target_px), 2),
        "stop_pct": stop_pct,
        "net_target": round(daily_goal, 2),
        "net_at_target": net_at_target,
        "net_at_stop": net_at_stop,
        "fees_round_trip": round_trip_fees(buy_fee, sell_fee),
    }


def validate_planned_trade(
    conn: sqlite3.Connection,
    *,
    ticker: str,
    planned_price: float,
    shares: float | None = None,
) -> dict:
    """Check whether a planned entry still matches live price and strategy rules."""
    sym = ticker.upper().strip()
    day_status = build_trading_day_status(conn)
    quotes = _latest_quote_rows(conn, [sym])
    live_q = quotes.get(sym)
    live_price = float(live_q["price"]) if live_q else None

    tradable = day_status.get("top_pick", {})  # for deploy hint
    pick = get_top_pick(conn)
    deploy = float(pick.get("suggested_size") or 0) if pick and pick.get("ticker") == sym else 0
    if deploy <= 0:
        from investment_agent.account import build_dashboard_summary

        deploy = build_dashboard_summary(conn).tradable_cash

    if shares is not None and shares > 0:
        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        plan = compute_trade_plan(
            entry_price=planned_price,
            deploy_dollar=planned_price * shares + DEFAULT_BUY_FEE,
            net_target=remaining or day_status["daily_target"],
        )
        plan["shares"] = int(shares)
        plan["notional"] = round(planned_price * shares, 2)
        plan["total_cost"] = round(plan["notional"] + DEFAULT_BUY_FEE, 2)
        stop_px = planned_price * (1 - STOP_PCT / 100)
        s = int(shares)
        daily_goal = remaining or day_status["daily_target"]
        target_px = sell_price_for_net_target(
            entry_price=planned_price,
            shares=s,
            net_target=daily_goal,
        )
        plan["target_price"] = round(target_px, 2)
        plan["stop_price"] = round(stop_px, 2)
        plan["target_pct"] = round(target_move_pct(planned_price, target_px), 2)
        plan["net_at_target"] = round(s * (target_px - planned_price) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
        plan["net_at_stop"] = round(s * (stop_px - planned_price) - DEFAULT_BUY_FEE - DEFAULT_SELL_FEE, 2)
    else:
        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        plan = compute_trade_plan(
            entry_price=planned_price,
            deploy_dollar=deploy,
            net_target=remaining or day_status["daily_target"],
        )

    checks: list[dict] = []
    verdict = "GO"
    messages: list[str] = []

    if not live_price:
        verdict = "CAUTION"
        messages.append("No live quote — refresh live data before buying.")
        checks.append({"name": "Live quote", "ok": False, "message": "Missing — click Refresh live data"})
    else:
        slippage = ((planned_price - live_price) / live_price) * 100.0
        if slippage > MAX_ENTRY_SLIPPAGE_PCT:
            verdict = "NO_GO"
            messages.append(f"Planned price ${planned_price:.2f} is {slippage:.2f}% above live ${live_price:.2f}.")
            checks.append({"name": "Price vs live", "ok": False, "message": f"+{slippage:.2f}% above live (max {MAX_ENTRY_SLIPPAGE_PCT}%)"})
        elif slippage < -MAX_ENTRY_SLIPPAGE_PCT:
            checks.append({"name": "Price vs live", "ok": True, "message": f"{slippage:+.2f}% vs live ${live_price:.2f}"})
        else:
            checks.append({"name": "Price vs live", "ok": True, "message": f"Within {slippage:+.2f}% of live ${live_price:.2f}"})

        remaining = max(day_status["daily_target"] - day_status.get("today_realized_net", 0), 0)
        goal = remaining or day_status["daily_target"]
        metrics_row = conn.execute(
            """
            SELECT avg_range_pct FROM ticker_metrics
            WHERE ticker = ?
            ORDER BY computed_at DESC LIMIT 1
            """,
            (sym,),
        ).fetchone()
        avg_range = float(metrics_row["avg_range_pct"]) if metrics_row and metrics_row["avg_range_pct"] else None
        hist = load_dollar_history(
            conn,
            sym,
            end_date=today_et_str(),
            deploy_dollar=deploy,
            net_target=goal,
        )
        trad = assess_entry_tradability(
            quote=live_q,
            entry_price=planned_price,
            deploy_dollar=deploy,
            net_target=goal,
            avg_range_pct=avg_range,
            dollar_history=hist,
        )
        if trad.get("verdict") == "NOT_TRADABLE":
            verdict = "NO_GO"
            messages.append(trad.get("detail") or "Not tradable for today's dollar target")
            checks.append({"name": "Tradability", "ok": False, "message": trad.get("detail", "Not tradable")})
        elif trad.get("verdict") == "CAUTION":
            if verdict == "GO":
                verdict = "CAUTION"
            checks.append({"name": "Tradability", "ok": None, "message": trad.get("detail", "Marginal")})
        elif trad.get("verdict") == "TRADABLE":
            checks.append({"name": "Tradability", "ok": True, "message": trad.get("detail", "Tradable for $ goal")})
        else:
            checks.append({"name": "Tradability", "ok": None, "message": trad.get("detail", "Unknown — refresh live data")})

    if pick and pick.get("ticker") != sym:
        if verdict == "GO":
            verdict = "CAUTION"
        messages.append(f"{sym} is not today's #1 pick ({pick.get('ticker')} is).")
        checks.append({"name": "Rank", "ok": False, "message": f"Not #1 — top pick is {pick.get('ticker')}"})
    elif pick:
        checks.append({"name": "Rank", "ok": True, "message": f"{sym} is today's ranked #1"})

    if day_status["verdict"] == "NO_GO":
        verdict = "NO_GO"
        messages.append(day_status["headline"])
        checks.append({"name": "Day status", "ok": False, "message": day_status["headline"]})
    elif day_status["verdict"] in ("CAUTION", "WAIT"):
        if verdict == "GO":
            verdict = "CAUTION"
        checks.append({"name": "Day status", "ok": None, "message": day_status["headline"]})
    else:
        checks.append({"name": "Day status", "ok": True, "message": day_status["headline"]})

    daily_target = day_status["daily_target"]
    if plan.get("net_at_target") is not None:
        goal = plan.get("net_target") or daily_target
        if plan["net_at_target"] >= goal * 0.98:
            checks.append({"name": "Target P&L", "ok": True, "message": f"Sell nets ~${plan['net_at_target']:.2f} (Growth Plan ${goal:.0f}/day)"})
        else:
            if verdict == "GO":
                verdict = "CAUTION"
            checks.append({"name": "Target P&L", "ok": None, "message": f"Sell nets ~${plan['net_at_target']:.2f} — below ${goal:.0f} day goal on this size"})

    if not plan:
        verdict = "NO_GO"
        messages.append("Could not size trade — check price and deploy amount.")

    headline = "Recommended — proceed in E*TRADE" if verdict == "GO" else (
        "Caution — review before buying" if verdict == "CAUTION" else "Not recommended — do not buy"
    )

    return {
        "verdict": verdict,
        "headline": headline,
        "messages": messages,
        "checks": checks,
        "ticker": sym,
        "planned_price": round(planned_price, 2),
        "live_price": round(live_price, 2) if live_price else None,
        "plan": plan,
        "day_status_verdict": day_status["verdict"],
    }


def _build_pick_detail(
    pick: dict,
    *,
    quote: dict | None,
    deploy: float,
    net_target: float,
) -> dict:
    avg_range = float(pick.get("avg_range_pct") or 0)
    session_open = _session_open_from_quote(
        quote,
        fallback=float(pick.get("session_open") or pick.get("entry_price") or 0) or None,
    )
    plan = pick if pick.get("limit_buy_price") else (
        compute_pullback_trade_plan(
            session_open=session_open or 0,
            avg_range_pct=avg_range,
            deploy_dollar=deploy,
            net_target=net_target,
        )
        if session_open
        else {}
    )
    if not plan and session_open:
        plan = compute_trade_plan(
            entry_price=session_open,
            deploy_dollar=deploy,
            net_target=net_target,
        )

    tradability = pick.get("tradability")
    limit_entry = plan.get("limit_buy_price") or plan.get("entry_price")
    if tradability is None and quote and limit_entry:
        hist = pick.get("dollar_history")
        tradability = assess_entry_tradability(
            quote=quote,
            entry_price=limit_entry,
            deploy_dollar=deploy,
            net_target=net_target,
            avg_range_pct=avg_range or None,
        )

    live_price = float(quote["price"]) if quote and quote.get("price") else None
    detail = {
        "ticker": pick["ticker"],
        "rank_score": pick.get("score"),
        "hit_rate_pct": pick.get("hit_rate_pct"),
        "source": pick.get("source"),
        "live_pass_today": bool(pick.get("live_pass_today")),
        "entry_mode": plan.get("entry_mode", "pullback_limit"),
        "session_open": plan.get("session_open"),
        "pullback_pct": plan.get("pullback_pct"),
        "limit_buy_price": plan.get("limit_buy_price"),
        "limit_sell_price": plan.get("limit_sell_price") or plan.get("target_price"),
        "limit_fill_deadline_et": plan.get("limit_fill_deadline_et"),
        "skip_if_not_filled_by": plan.get("skip_if_not_filled_by"),
        "recommended_entry": plan.get("limit_buy_price") or plan.get("entry_price"),
        "entry_price": plan.get("limit_buy_price") or plan.get("entry_price"),
        "target_price": plan.get("target_price"),
        "stop_price": plan.get("stop_price"),
        "target_pct": plan.get("target_pct"),
        "recommended_shares": plan.get("shares"),
        "notional": plan.get("notional"),
        "total_cost": plan.get("total_cost"),
        "net_target": plan.get("net_target"),
        "net_at_target": plan.get("net_at_target"),
        "net_at_stop": plan.get("net_at_stop"),
        "suggested_size": deploy,
        "quote_price": live_price,
        "quote_as_of": quote.get("captured_at") if quote else None,
        "thesis_summary": pick.get("thesis_summary"),
        "tradability": tradability,
        "dollar_hit_rate_pct": pick.get("dollar_hit_rate_pct")
        or (tradability or {}).get("dollar_hit_rate_pct"),
        "dollar_confidence": pick.get("dollar_confidence")
        or dollar_confidence(float(pick.get("dollar_hit_rate_pct") or 0)),
        "expected_net_at_typical_high": plan.get("estimated_net_at_typical_high")
        or (tradability or {}).get("expected_net_at_typical_high"),
        "historical_avg_net_at_high": (tradability or {}).get("historical_avg_net_at_high"),
        "dollar_history": pick.get("dollar_history"),
        "dollar_prediction": (tradability or {}).get("dollar_prediction"),
    }
    return detail


def build_trading_day_status(conn: sqlite3.Connection) -> dict:
    """Go/no-go panel for intraday manual trading."""
    now = now_et()
    phase = session_phase(now)
    summary = build_dashboard_summary(conn)
    day = today_et_str()
    today_net = compute_today_realized_net(conn, day)
    daily_target = summary.daily_target
    target_met = today_net >= daily_target
    stopped = stopped_out_today(conn, day)
    open_positions = get_open_positions(conn)
    remaining_net = max(daily_target - today_net, 0)
    net_for_plan = remaining_net or daily_target

    watch: list[str] = list(REGIME_SYMBOLS)
    for row in _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN):
        watch.append(row["ticker"])
    quotes = _latest_quote_rows(conn, watch)

    pick, skipped_picks = resolve_actionable_pick(
        conn,
        quotes=quotes,
        deploy=summary.tradable_cash,
        net_target=net_for_plan,
    )
    ranked_first = get_top_pick(conn)

    regime_quote_ages = [
        _quote_age_minutes(quotes[s]["captured_at"])
        for s in REGIME_SYMBOLS
        if s in quotes
    ]
    max_age = max(regime_quote_ages) if regime_quote_ages else None
    quotes_stale = max_age is None or max_age > QUOTE_STALE_MINUTES

    pick_quote = quotes.get(pick["ticker"]) if pick else None
    pick_change = _intraday_change_pct(pick_quote) if pick_quote else None
    pick_range = _opening_range_pct(pick_quote) if pick_quote else None

    checks: list[dict] = []
    verdict = "GO"
    headline = "Good to trade"
    detail = "Conditions favor taking the top ranked setup after the 30-minute gate."

    def add_check(name: str, ok: bool | None, message: str, *, blocking: bool = False):
        checks.append({"name": name, "ok": ok, "message": message, "blocking": blocking})

    if phase == "weekend":
        verdict = "NO_GO"
        headline = "Market closed (weekend)"
        detail = "No intraday session — review ranked list for Monday."
        add_check("Session", False, "Weekend — market closed", blocking=True)
    elif phase == "pre_market":
        verdict = "WAIT"
        headline = "Pre-market — wait for open"
        detail = f"Market opens 9:30 AM ET. First entry window after {ENTRY_READY.strftime('%H:%M')} ET ({ENTRY_DELAY_MINUTES} min delay)."
        add_check("Session", None, "Pre-market", blocking=True)
    elif phase == "opening_wait":
        verdict = "WAIT"
        headline = "Opening period — wait for 30-minute gate"
        mins_left = int(
            (
                datetime.combine(now.date(), ENTRY_READY, tzinfo=ET) - now
            ).total_seconds()
            // 60
        )
        detail = f"Let the opening chop settle. Entry gate opens in ~{max(mins_left, 0)} min (10:00 AM ET)."
        add_check("30-minute gate", None, f"Wait until {ENTRY_READY.strftime('%H:%M')} ET", blocking=True)
    elif phase in ("late_day", "after_hours"):
        verdict = "NO_GO"
        headline = "Too late for new entries"
        detail = f"Entry window was {ENTRY_WINDOW_ET} ET. Manage open positions only."
        add_check("Entry window", False, "Past 2:30 PM ET cutoff", blocking=True)
    else:
        add_check(
            "30-minute gate",
            True,
            f"Past {ENTRY_READY.strftime('%H:%M')} ET — opening period complete",
        )
        add_check("Entry window", True, f"Within {ENTRY_WINDOW_ET} ET window")

    if summary.block_new_longs:
        verdict = "NO_GO"
        headline = "Regime blocks new longs"
        detail = summary.regime["summary"] if summary.regime else "SPY/DIA/QQQ all down intraday."
        add_check("Regime", False, detail, blocking=True)
    elif phase in ("trade_window", "opening_wait", "pre_market"):
        regime_msg = summary.regime["summary"] if summary.regime else "Run refresh for live regime"
        add_check("Regime", True, regime_msg)

    if quotes_stale:
        if verdict == "GO":
            verdict = "CAUTION"
        headline = headline if verdict != "GO" else "Refresh live data"
        detail = "Quote data is stale — click Refresh live before deciding."
        add_check(
            "Live quotes",
            False,
            f"Last quote {max_age:.0f} min ago (refresh needed)" if max_age else "No quotes — run refresh",
            blocking=False,
        )
    else:
        add_check("Live quotes", True, f"Updated within {max_age:.0f} min")

    if target_met:
        verdict = "NO_GO"
        headline = "Daily target hit — stop trading"
        detail = f"Today net ${today_net:,.2f} ≥ ${daily_target:,.0f} goal. Protect the green day."
        add_check("Daily target", True, f"${today_net:,.2f} / ${daily_target:,.0f}", blocking=True)
    else:
        remaining = daily_target - today_net
        add_check(
            "Daily target",
            None,
            f"${today_net:,.2f} of ${daily_target:,.2f} (${remaining:,.2f} to go)",
        )

    if stopped:
        verdict = "NO_GO"
        headline = "Stop-out day — done for today"
        detail = "A losing round trip was logged today. No revenge trades."
        add_check("Stop-out rule", False, "Loss logged today — no more entries", blocking=True)
    else:
        add_check("Stop-out rule", True, "No stop-out logged today")

    if open_positions:
        if verdict == "GO":
            verdict = "CAUTION"
        pos = open_positions[0]
        detail = f"Open position in {pos['ticker']} — finish before a new full-size entry."
        add_check(
            "Open position",
            None,
            f"{pos['ticker']}: {pos['shares']:.0f} sh @ ${pos['avg_cost']:.2f}",
        )
    else:
        add_check("Open position", True, "Flat — ready for one full-size entry")

    if pick is None:
        if verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
        if skipped_picks:
            skipped_names = ", ".join(s["ticker"] for s in skipped_picks[:5])
            headline = "No tradable setup for today's $ goal"
            detail = (
                f"Step 3 passers fail live tradability for ${net_for_plan:.0f} net: "
                f"{skipped_names}"
                + (f" +{len(skipped_picks) - 5} more" if len(skipped_picks) > 5 else "")
            )
            add_check("Top pick", False, detail, blocking=True)
        else:
            headline = "No live top pick"
            detail = "No ticker passes Step 3 today — run ingest and refresh ranked screener."
            add_check("Top pick", False, "No live Step 3 candidates today", blocking=True)
    else:
        pick_ok = True
        pick_msg = (
            f"{pick['ticker']} (score {pick.get('score', 0):.3f}, "
            f"${pick.get('dollar_hit_rate_pct', 0):.0f}% $ hit, "
            f"{pick.get('hit_rate_pct', 0):.0f}% 1.5% hit)"
        )
        if not pick.get("live_pass_today"):
            pick_ok = False
            pick_msg += " — not live Step 3 today"
        if pick_change is not None:
            pick_msg += f" · {pick_change:+.2f}% from open"
            if pick_change <= -TOP_PICK_NO_GO_DROP_PCT:
                pick_ok = False
                if verdict == "GO":
                    verdict = "NO_GO"
                headline = f"{pick['ticker']} weak at open"
                detail = f"Top pick down {pick_change:.2f}% from open — skip or wait for next ranked name."
            elif pick_change <= -TOP_PICK_MAX_DROP_PCT:
                pick_ok = False
                if verdict == "GO":
                    verdict = "CAUTION"
                detail = f"{pick['ticker']} slightly weak ({pick_change:+.2f}%) — extra caution."
        if pick_range is not None and pick_range < 0.4 and phase == "trade_window":
            pick_msg += f" · tight {pick_range:.2f}% range (chop)"

        trad = (pick.get("tradability") or {}) if pick else {}
        trad_verdict = trad.get("verdict")
        if trad_verdict == "NOT_TRADABLE":
            pick_ok = False
            if verdict == "GO":
                verdict = "NO_GO"
            headline = f"{pick['ticker']} — not tradable for ${net_for_plan:.0f}"
            detail = trad.get("detail") or "Insufficient room from entry to Growth Plan sell target."
            pick_msg += f" · NOT TRADABLE: {trad.get('detail', '')[:80]}"
        elif trad_verdict == "CAUTION":
            pick_ok = False
            if verdict == "GO":
                verdict = "CAUTION"
            detail = trad.get("detail") or detail
            pick_msg += f" · CAUTION: {trad.get('detail', '')[:80]}"
        elif trad_verdict == "TRADABLE":
            pick_msg += " · limit entry tradable for $ goal"

        add_check("Top pick", pick_ok if pick_ok else False, pick_msg, blocking=not pick_ok and pick_change is not None and pick_change <= -TOP_PICK_NO_GO_DROP_PCT)

    if skipped_picks:
        skipped_names = ", ".join(s["ticker"] for s in skipped_picks[:3])
        add_check(
            "Skipped (not tradable)",
            None,
            f"{skipped_names}" + (f" +{len(skipped_picks) - 3} more" if len(skipped_picks) > 3 else ""),
        )

    if summary.vix is not None and summary.vix >= 22:
        if verdict == "GO":
            verdict = "CAUTION"
        add_check("VIX", False, f"VIX {summary.vix:.1f} — elevated volatility")
    elif summary.vix is not None:
        add_check("VIX", True, f"VIX {summary.vix:.1f}")

    # Second trade only if target not met and no stop
    can_second_trade = (
        not target_met
        and not stopped
        and not summary.block_new_longs
        and phase == "trade_window"
        and today_net > 0
        and not open_positions
    )

    pick_detail = None
    second_pick_detail = None
    if pick:
        pick_quote = quotes.get(pick["ticker"])
        pick_detail = _build_pick_detail(
            pick,
            quote=pick_quote,
            deploy=float(pick.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
        )
        if pick_change is not None:
            pick_detail["intraday_change_pct"] = round(pick_change, 3)
        if pick_range is not None:
            pick_detail["opening_range_pct"] = round(pick_range, 3)
        if pick_detail and pick_quote:
            limit_px = pick_detail.get("limit_buy_price")
            day_low = pick_quote.get("low")
            if limit_fill_missed(
                limit_buy_price=float(limit_px or 0),
                session_low=float(day_low) if day_low is not None else None,
                as_of_time=now.time(),
            ):
                verdict = "NO_GO"
                headline = f"{pick['ticker']} — pullback limit not filled"
                detail = (
                    f"Limit buy ${limit_px:.2f} was not reached by {LIMIT_FILL_DEADLINE.strftime('%H:%M')} ET "
                    "— skip today, do not chase with a market order."
                )
                add_check(
                    "Limit fill",
                    False,
                    detail,
                    blocking=True,
                )
            elif limit_px and day_low is not None and day_low <= limit_px:
                add_check(
                    "Limit fill",
                    True,
                    f"Session low ${day_low:.2f} touched limit ${limit_px:.2f} — limit may have filled",
                )
            elif limit_px:
                add_check(
                    "Limit fill",
                    None,
                    f"Place limit buy ${limit_px:.2f} · cancel if not filled by 11:30 ET",
                )

    # Second pick: next tradable live name after actionable #1
    second_candidates = _live_ranked_candidates(conn, limit=ACTIONABLE_PICK_SCAN)
    if pick:
        second_candidates = [r for r in second_candidates if r["ticker"] != pick["ticker"]]
    second_row = None
    for row in second_candidates:
        sym = row["ticker"]
        quote = quotes.get(sym)
        if not quote or not quote.get("price"):
            continue
        plan, t, hist_dict = _assess_pick_tradability(
            row,
            quote,
            deploy=float(row.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
            conn=conn,
        )
        if t.get("verdict") == "TRADABLE":
            second_row = {
                **row,
                **plan,
                "tradability": t,
                "dollar_history": hist_dict,
                "source": "ranked_#2",
            }
            break

    if second_row:
        second_quote = quotes.get(second_row["ticker"])
        second_pick_detail = _build_pick_detail(
            second_row,
            quote=second_quote,
            deploy=float(second_row.get("suggested_size") or summary.tradable_cash),
            net_target=net_for_plan,
        )

    return {
        "as_of_et": now.replace(microsecond=0).isoformat(),
        "date_et": day,
        "session_phase": phase,
        "verdict": verdict,
        "headline": headline,
        "detail": detail,
        "checks": checks,
        "today_realized_net": round(today_net, 2),
        "daily_target": daily_target,
        "daily_target_met": target_met,
        "stopped_out_today": stopped,
        "can_enter_new": verdict == "GO" and not open_positions and not target_met and not stopped,
        "can_second_trade": can_second_trade,
        "open_positions": open_positions,
        "top_pick": pick_detail,
        "second_pick": second_pick_detail,
        "ranked_first": ranked_first["ticker"] if ranked_first else None,
        "skipped_not_tradable": skipped_picks,
        "next_ranked": _next_ranked(conn, pick["ticker"] if pick else None),
        "remaining_daily_net": round(remaining_net, 2),
        "strategy": {
            "daily_net_target": daily_target,
            "stop_pct": STOP_PCT,
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "entry_window_et": ENTRY_WINDOW_ET,
        },
    }


def _next_ranked(conn: sqlite3.Connection, after_ticker: str | None) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=14)["ranked"]
    live = [r for r in ranked if r.get("live_pass_today")]
    if after_ticker:
        live = [r for r in live if r["ticker"] != after_ticker]
    return [
        {
            "ticker": r["ticker"],
            "rank_score": r.get("score"),
            "hit_rate_pct": r.get("hit_rate_pct"),
            "dollar_hit_rate_pct": r.get("dollar_hit_rate_pct"),
        }
        for r in live[:5]
    ]


def pin_top_pick(conn: sqlite3.Connection, ticker: str) -> dict:
    sym = ticker.upper().strip()
    set_setting(conn, "pinned_pick_ticker", sym)
    return {"ok": True, "pinned_pick_ticker": sym}


def clear_pinned_pick(conn: sqlite3.Connection) -> dict:
    set_setting(conn, "pinned_pick_ticker", "")
    return {"ok": True, "pinned_pick_ticker": ""}
