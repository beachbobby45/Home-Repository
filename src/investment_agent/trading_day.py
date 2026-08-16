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
    weekly_production_target,
)
from investment_agent.journal import (
    compute_today_realized_net,
    compute_weekly_realized_net,
    count_weekly_production_opportunities,
    get_completed_round_trips,
    get_open_positions,
    open_position_for_ticker,
    today_pt_str,
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
from investment_agent.risk_engine import (
    MarketSnapshot,
    auto_engaged_kill_switch,
    build_portfolio_snapshot,
    evaluate_proposal_from_plan_dict,
    portfolio_allows_new_entries,
    portfolio_status_dict,
    risk_decision_to_dict,
)

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
    block_new_longs: bool = False,
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
        conn=conn,
        ticker=row["ticker"],
        block_new_longs=block_new_longs,
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


EXTENDED_SESSION_PHASES = frozenset({"pre_market", "after_hours", "weekend"})
EXTENDED_SESSION_LABELS = {
    "pre_market": "Pre-market",
    "after_hours": "After hours",
    "weekend": "Weekend (last quote)",
}
NEAR_STOP_CUSHION_PCT = 0.35


def _rth_close_for_date(
    conn: sqlite3.Connection,
    ticker: str,
    date_et: str,
) -> float | None:
    row = conn.execute(
        "SELECT close FROM ohlcv_daily WHERE ticker = ? AND date = ?",
        (ticker.upper(), date_et),
    ).fetchone()
    if not row or row["close"] is None:
        return None
    return float(row["close"])


def build_extended_session(
    *,
    phase: str,
    quote: dict | None,
    limit_buy: float | None,
    stop_price: float | None,
    limit_sell: float | None,
    shares: int | None = None,
    rth_close: float | None = None,
    from_journal: bool = False,
    journal_entry_price: float | None = None,
    journal_shares: int | None = None,
) -> dict | None:
    """Extended-hours context for the live pick card (RTH estimates unchanged)."""
    if phase not in EXTENDED_SESSION_PHASES:
        return None
    if not quote or quote.get("price") is None:
        return None

    price = float(quote["price"])
    entry_price = journal_entry_price or limit_buy
    position_shares = journal_shares or shares

    position_flags: list[dict] = []
    if stop_price and price <= stop_price:
        position_flags.append(
            {
                "id": "at_or_below_stop",
                "severity": "danger",
                "text": f"At/below stop ${stop_price:.2f}",
            }
        )
    elif stop_price and stop_price > 0:
        cushion_pct = ((price - stop_price) / stop_price) * 100.0
        if 0 < cushion_pct <= NEAR_STOP_CUSHION_PCT:
            position_flags.append(
                {
                    "id": "near_stop",
                    "severity": "warn",
                    "text": f"Near stop ${stop_price:.2f} ({cushion_pct:.2f}% cushion)",
                }
            )

    if limit_sell and price >= limit_sell:
        position_flags.append(
            {
                "id": "at_or_above_target",
                "severity": "ok",
                "text": f"At/above limit sell ${limit_sell:.2f}",
            }
        )

    if limit_buy and price < limit_buy:
        position_flags.append(
            {
                "id": "below_limit_entry",
                "severity": "info",
                "text": f"Below limit entry ${limit_buy:.2f}",
            }
        )

    if phase == "weekend":
        position_flags.append(
            {
                "id": "weekend_gap_risk",
                "severity": "warn",
                "text": "Weekend hold — gap risk at next open (news can move price)",
            }
        )

    reference_label = None
    reference_price = None
    if phase == "pre_market":
        reference_price = quote.get("prev_close")
        reference_label = "prior close"
    elif phase in ("after_hours", "weekend") and rth_close and rth_close > 0:
        reference_price = rth_close
        reference_label = "RTH close"
    elif phase in ("after_hours", "weekend"):
        reference_price = quote.get("prev_close")
        reference_label = "prior close"

    change_vs_reference_pct = None
    if reference_price and reference_price > 0:
        change_vs_reference_pct = round(
            ((price - reference_price) / reference_price) * 100.0,
            3,
        )

    change_vs_entry_pct = None
    if entry_price and entry_price > 0:
        change_vs_entry_pct = round(((price - entry_price) / entry_price) * 100.0, 3)

    net_if_sold_now = None
    if position_shares and entry_price and position_shares > 0:
        net_if_sold_now = round(
            position_shares * (price - entry_price) - round_trip_fees(),
            2,
        )

    entry_label = f"journal ${entry_price:.2f}" if from_journal and journal_entry_price else "limit entry"

    return {
        "label": EXTENDED_SESSION_LABELS.get(phase, phase.replace("_", " ").title()),
        "phase": phase,
        "price": round(price, 2),
        "quote_as_of": quote.get("captured_at"),
        "change_vs_reference_pct": change_vs_reference_pct,
        "reference_label": reference_label,
        "note": "RTH plan and estimates above are unchanged — extended quote for monitoring only.",
        "fill_status": {
            "from_journal": from_journal,
            "default_assume_filled": from_journal,
            "entry_price": round(entry_price, 2) if entry_price else None,
            "entry_label": entry_label,
            "shares": int(position_shares) if position_shares else None,
        },
        "position": {
            "change_vs_entry_pct": change_vs_entry_pct,
            "entry_label": entry_label,
            "net_if_sold_now": net_if_sold_now,
            "flags": position_flags,
        },
        "not_filled_hint": (
            "Limit not assumed filled — toggle Filled to monitor stop/target vs entry, "
            "or log a BUY in the journal."
        ),
    }


def get_top_pick(conn: sqlite3.Connection) -> dict | None:
    """Highest ranked live candidate that passes the dollar-goal rank gate."""
    pinned = get_setting(conn, "pinned_pick_ticker", "").strip().upper()
    ranked = build_ranked_candidates(conn, period_days=14, require_opportunity_floor=True)["ranked"]
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
    ranked = build_ranked_candidates(conn, period_days=14, require_opportunity_floor=True)["ranked"]
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
    block_new_longs: bool = False,
    confirmation_filter: callable | None = None,
) -> tuple[dict | None, list[dict]]:
    """Pick first live ranked name that passes intraday tradability for today's $ goal."""
    skipped: list[dict] = []
    candidates = _live_ranked_candidates(conn)

    for idx, row in enumerate(candidates):
        sym = row["ticker"]
        if confirmation_filter is not None and not confirmation_filter(sym, idx):
            skipped.append({
                "ticker": sym,
                "rank_score": row.get("score"),
                "reason": "Confirmation below threshold or rank not eligible today",
                "verdict": "NOT_CONFIRMED",
            })
            continue
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
            row, quote, deploy=deploy, net_target=net_target, conn=conn,
            block_new_longs=block_new_longs,
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
    quote_rows: dict[str, dict] = {}

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
                captured = fh_now()
                row = {
                    "ticker": symbol,
                    "captured_at": captured,
                    "price": float(q["c"]),
                    "open": float(q.get("o") or 0) or None,
                    "high": float(q.get("h") or 0) or None,
                    "low": float(q.get("l") or 0) or None,
                    "prev_close": float(q.get("pc") or 0) or None,
                    "source": "finnhub",
                }
                insert_quote(conn, row)
                quote_rows[symbol] = row
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

    from investment_agent.quote_snapshots import maybe_record_snapshots_after_refresh

    snapshot = maybe_record_snapshots_after_refresh(conn, quote_rows)

    from investment_agent.market_activity import evaluate_market_activity

    market_activity = evaluate_market_activity(conn, persist=True)

    from investment_agent.confirmation import evaluate_session_confirmations

    confirmations = evaluate_session_confirmations(
        conn,
        market_activity=market_activity,
        live_quotes=quote_rows,
        persist=True,
    )

    from investment_agent.decision_attribution import log_decision_attribution
    from investment_agent.market_activity import market_activity_to_dict

    ma_payload = market_activity_to_dict(market_activity)
    top_conf = confirmations[0] if confirmations else None
    log_decision_attribution(
        conn,
        event_type="live_refresh",
        market_activity=ma_payload,
        confirmation=top_conf,
        detail={"confirmation_count": len(confirmations)},
    )

    return {
        "ok": len(updated) > 0,
        "updated": updated,
        "errors": errors,
        "symbols_requested": sorted(symbols),
        "snapshot": snapshot,
        "market_activity": market_activity,
        "confirmations": confirmations,
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
            conn=conn,
            ticker=sym,
            block_new_longs=day_status.get("block_new_longs", False),
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

    from investment_agent.confirmation import (
        _rank_eligible,
        confirmations_to_dict,
        evaluate_session_confirmations,
    )
    from investment_agent.market_activity import evaluate_market_activity, market_activity_to_dict

    market_activity = market_activity_to_dict(evaluate_market_activity(conn, when=now, persist=False))
    confirmations = confirmations_to_dict(
        evaluate_session_confirmations(
            conn,
            market_activity=market_activity,
            live_quotes=quotes,
            when=now,
        )
    )

    confirmation_filter = None
    if market_activity.get("allow_trade"):
        conf_map = {item["ticker"]: item for item in confirmations}
        market_band = market_activity.get("band")

        def confirmation_filter(ticker: str, rank_index: int) -> bool:
            if not _rank_eligible(rank_index, market_band):
                return False
            item = conf_map.get(ticker)
            return bool(item and item.get("passes"))

    pick, skipped_picks = resolve_actionable_pick(
        conn,
        quotes=quotes,
        deploy=summary.tradable_cash,
        net_target=net_for_plan,
        block_new_longs=summary.block_new_longs,
        confirmation_filter=confirmation_filter,
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

    portfolio_snapshot = build_portfolio_snapshot(conn)
    if auto_engaged_kill_switch(conn, portfolio_snapshot):
        portfolio_snapshot = build_portfolio_snapshot(conn)
    regime_summary = summary.regime["summary"] if summary.regime else None
    portfolio_risk = portfolio_allows_new_entries(
        conn,
        block_new_longs=summary.block_new_longs,
        regime_summary=regime_summary,
    )
    risk_status = portfolio_status_dict(portfolio_snapshot)

    weekly_target = weekly_production_target(float(summary.tradable_cash or 0))
    pt_day = today_pt_str()
    weekly_net = compute_weekly_realized_net(conn, pt_day)
    weekly_target_met = weekly_net >= weekly_target
    weekly_opportunities = 3
    opportunities_used = count_weekly_production_opportunities(
        conn, date_key=pt_day, daily_target=daily_target
    )

    from investment_agent.exceptional_trade import (
        count_exceptional_trades_consumed,
        evaluate_exceptional_trade,
        exceptional_trade_to_dict,
    )

    exceptional_consumed = count_exceptional_trades_consumed(conn, date_key=pt_day)
    exceptional = exceptional_trade_to_dict(
        evaluate_exceptional_trade(
            weekly_target_met=weekly_target_met,
            market_activity=market_activity,
            confirmations=confirmations,
            pick_ticker=pick["ticker"] if pick else None,
            phase=phase,
            stopped=stopped,
            open_positions_count=len(open_positions),
            portfolio_risk_verdict=portfolio_risk.verdict,
            exceptional_consumed_this_week=exceptional_consumed,
        )
    )

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

    ma_summary = market_activity.get("summary") or "Market Activity pending"
    if not market_activity.get("allow_trade"):
        add_check(
            "Market Activity",
            False,
            f"{market_activity.get('score', 0)}/100 — {market_activity.get('band_label', 'blocked')} · NO TRADE",
            blocking=phase == "trade_window",
        )
        if phase == "trade_window" and verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
            headline = "DO NOT TRADE TODAY"
            detail = ma_summary
        elif phase in ("opening_wait", "pre_market"):
            detail = f"{detail} · Preliminary: {ma_summary}"
    else:
        add_check(
            "Market Activity",
            True,
            f"{market_activity.get('score', 0)}/100 — {market_activity.get('band_label', 'ok')} · entries allowed",
        )

    if market_activity.get("allow_trade") and phase == "trade_window":
        confirmed = [c for c in confirmations if c.get("passes") and c.get("eligible")]
        if pick and pick.get("ticker"):
            pick_conf = next((c for c in confirmations if c.get("ticker") == pick["ticker"]), None)
            if pick_conf:
                add_check(
                    "Confirmation",
                    True,
                    f"{pick['ticker']} {pick_conf.get('score', 0)}/100 — PASS",
                )
            else:
                add_check("Confirmation", False, f"{pick['ticker']} — no confirmation score", blocking=True)
        elif confirmed:
            add_check(
                "Confirmation",
                None,
                "Names confirm but none tradable for today's $ goal",
            )
        else:
            top = confirmations[0] if confirmations else None
            if top:
                if verdict in ("GO", "CAUTION"):
                    verdict = "NO_GO"
                headline = "No confirming setup"
                detail = top.get("summary") or f"Ranked #{top.get('rank')} below {75} confirmation threshold"
                add_check(
                    "Confirmation",
                    False,
                    detail,
                    blocking=True,
                )

    if market_activity.get("exit_alert") and open_positions:
        pos = open_positions[0]
        exit_msg = market_activity.get("flip_reason") or "Day flipped NO TRADE — sell at market"
        add_check(
            "Exit alert",
            False,
            f"{exit_msg} ({pos['ticker']} open)",
            blocking=True,
        )
        if verdict == "GO":
            verdict = "NO_GO"
        headline = "EXIT AT MARKET"
        detail = exit_msg

    for risk_check in portfolio_risk.checks:
        add_check(
            risk_check["name"],
            risk_check["ok"],
            risk_check["message"],
            blocking=bool(risk_check.get("blocking")),
        )
    if portfolio_risk.verdict == "rejected":
        verdict = "NO_GO"
        headline = portfolio_risk.headline
        detail = portfolio_risk.blockers[0] if portfolio_risk.blockers else portfolio_risk.headline

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

    if target_met and not exceptional.get("active"):
        verdict = "NO_GO"
        headline = "Daily target hit — stop trading"
        detail = f"Today net ${today_net:,.2f} ≥ ${daily_target:,.0f} goal. Protect the green day."
        add_check("Daily target", True, f"${today_net:,.2f} / ${daily_target:,.0f}", blocking=True)
    elif target_met and exceptional.get("active"):
        add_check(
            "Daily target",
            None,
            f"${today_net:,.2f} / ${daily_target:,.0f} — exceptional override allows 1 more trade",
        )
    else:
        remaining = daily_target - today_net
        add_check(
            "Daily target",
            None,
            f"${today_net:,.2f} of ${daily_target:,.2f} (${remaining:,.2f} to go)",
        )

    if weekly_target_met and not exceptional.get("active"):
        if verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
        headline = "Weekly target met — stop for the week"
        detail = (
            f"Week net ${weekly_net:,.0f} ≥ ${weekly_target:,.0f} guidance. "
            "Default stop — no new trades unless Exceptional override applies."
        )
        add_check(
            "Weekly guidance",
            True,
            f"${weekly_net:,.0f} / ${weekly_target:,.0f} · {opportunities_used} of {weekly_opportunities} opportunities",
            blocking=True,
        )
    elif weekly_target_met and exceptional.get("active"):
        if verdict in ("NO_GO", "CAUTION"):
            verdict = "GO"
        headline = "Exceptional override — 1 extra trade allowed"
        detail = exceptional.get("summary") or (
            "Weekly guidance met — Exceptional day + confirmation PASS unlocks one more trade."
        )
        add_check(
            "Weekly guidance",
            True,
            f"${weekly_net:,.0f} / ${weekly_target:,.0f} met — Exceptional override active (max 1/week)",
        )
    else:
        add_check(
            "Weekly guidance",
            None,
            f"${weekly_net:,.0f} of ${weekly_target:,.0f} · {opportunities_used} of {weekly_opportunities} opportunities",
        )

    if exceptional.get("active"):
        add_check("Exceptional override", True, exceptional.get("summary") or "Active")
    elif weekly_target_met and exceptional.get("eligible"):
        add_check(
            "Exceptional override",
            None,
            "Partial signals — not all GO for exceptional trade",
        )

    if stopped:
        verdict = "NO_GO"
        headline = "Stop-out day — done for today"
        detail = "A losing round trip was logged today. No revenge trades."
        add_check("Stop-out rule", False, "Loss logged today — no more entries", blocking=True)
    else:
        add_check("Stop-out rule", True, "No stop-out logged today")

    if open_positions:
        pos_count = len(open_positions)
        if pos_count >= 2:
            if verdict == "GO":
                verdict = "NO_GO"
            pos = open_positions[0]
            detail = (
                f"{pos_count} open positions (max 2) — manage existing before new entries."
            )
            add_check(
                "Open position",
                False,
                f"{pos_count} open — at max {2} positions",
                blocking=True,
            )
        else:
            pos = open_positions[0]
            add_check(
                "Open position",
                True,
                f"{pos['ticker']}: {pos['shares']:.0f} sh @ ${pos['avg_cost']:.2f} "
                f"({pos_count}/2 slots used)",
            )
    else:
        add_check("Open position", True, "Flat — ready for one full-size entry")

    if pick is None:
        if verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
        if skipped_picks:
            skipped_names = ", ".join(s["ticker"] for s in skipped_picks[:5])
            trad_detail = (
                f"Step 3 passers fail live tradability for ${net_for_plan:.0f} net: "
                f"{skipped_names}"
                + (f" +{len(skipped_picks) - 5} more" if len(skipped_picks) > 5 else "")
            )
            if phase != "weekend":
                headline = "No tradable setup for today's $ goal"
                detail = trad_detail
            add_check("Top pick", False, trad_detail, blocking=True)
        else:
            if phase != "weekend":
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
        (not target_met or exceptional.get("active"))
        and not stopped
        and not summary.block_new_longs
        and phase == "trade_window"
        and today_net > 0
        and not open_positions
        and not weekly_target_met
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
        pick_conf = next((c for c in confirmations if c.get("ticker") == pick["ticker"]), None)
        if pick_conf:
            pick_detail["confirmation_score"] = pick_conf.get("score")
            pick_detail["confirmation_passes"] = pick_conf.get("passes")
        open_pos = open_position_for_ticker(conn, pick["ticker"])
        ext = build_extended_session(
            phase=phase,
            quote=pick_quote,
            limit_buy=pick_detail.get("limit_buy_price"),
            stop_price=pick_detail.get("stop_price"),
            limit_sell=pick_detail.get("limit_sell_price"),
            shares=pick_detail.get("recommended_shares"),
            rth_close=_rth_close_for_date(conn, pick["ticker"], day),
            from_journal=open_pos is not None,
            journal_entry_price=float(open_pos["avg_cost"]) if open_pos else None,
            journal_shares=int(open_pos["shares"]) if open_pos else None,
        )
        if ext:
            pick_detail["extended_session"] = ext
            pick_detail["show_rth_live_quote"] = False
        else:
            pick_detail["show_rth_live_quote"] = True

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
            block_new_longs=summary.block_new_longs,
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

    from investment_agent.quote_snapshots import get_session_snapshot_status

    quote_snapshot_status = get_session_snapshot_status(conn, day)

    pick_risk = None
    if pick_detail and pick_detail.get("stop_price") and pick_detail.get("limit_buy_price"):
        pick_risk = evaluate_proposal_from_plan_dict(
            plan=pick_detail,
            ticker=pick_detail["ticker"],
            portfolio=portfolio_snapshot,
            market=MarketSnapshot(
                block_new_longs=summary.block_new_longs,
                regime_summary=regime_summary,
            ),
        )
        if pick_risk.verdict == "rejected" and verdict in ("GO", "CAUTION"):
            verdict = "NO_GO"
            headline = f"{pick_detail['ticker']} — risk engine rejected"
            detail = pick_risk.blockers[0] if pick_risk.blockers else pick_risk.headline
            add_check("Proposal risk", False, detail, blocking=True)

    show_no_trade_banner = (
        phase in ("trade_window", "opening_wait", "pre_market")
        and (
            not market_activity.get("allow_trade")
            or headline in ("DO NOT TRADE TODAY", "No confirming setup")
        )
    )
    exit_ticker = open_positions[0]["ticker"] if open_positions else None
    show_exit_alert = bool(market_activity.get("exit_alert") and open_positions)
    exit_message = market_activity.get("flip_reason") or (
        "Market Activity flipped NO TRADE — sell at market to exit"
    )

    phase1b = {
        "show_no_trade_banner": show_no_trade_banner,
        "no_trade_headline": "DO NOT TRADE TODAY" if show_no_trade_banner else None,
        "no_trade_detail": (
            market_activity.get("summary")
            if not market_activity.get("allow_trade")
            else detail
        )
        if show_no_trade_banner
        else None,
        "show_exit_alert": show_exit_alert,
        "exit_alert_headline": "EXIT — sell at market" if show_exit_alert else None,
        "exit_alert_message": exit_message if show_exit_alert else None,
        "exit_ticker": exit_ticker,
        "weekly_progress": {
            "opportunities_used": opportunities_used,
            "opportunities_target": weekly_opportunities,
            "weekly_realized_net": round(weekly_net, 2),
            "weekly_production_target": round(weekly_target, 2),
            "weekly_target_met": weekly_net >= weekly_target,
            "label": (
                f"{opportunities_used} of {weekly_opportunities} · "
                f"${weekly_net:,.0f} / ${weekly_target:,.0f}"
            ),
        },
        "market_activity_components": market_activity.get("components") or {},
        "block_new_proposals": phase == "trade_window" and not market_activity.get("allow_trade"),
        "exceptional_trade": exceptional,
        "show_exceptional_banner": bool(exceptional.get("active")),
        "exceptional_headline": (
            "EXCEPTIONAL OVERRIDE — 1 extra trade this week"
            if exceptional.get("active")
            else None
        ),
        "exceptional_detail": exceptional.get("summary") if exceptional.get("active") else None,
    }

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
        "can_enter_new": (
            verdict == "GO"
            and len(open_positions) < 2
            and (not target_met or exceptional.get("active"))
            and (not weekly_target_met or exceptional.get("active"))
            and not stopped
            and portfolio_risk.verdict == "approved"
            and market_activity.get("allow_trade")
            and (
                not confirmation_filter
                or (pick and pick.get("ticker"))
            )
        ),
        "can_second_trade": can_second_trade,
        "open_positions": open_positions,
        "top_pick": pick_detail,
        "second_pick": second_pick_detail,
        "ranked_first": ranked_first["ticker"] if ranked_first else None,
        "skipped_not_tradable": skipped_picks,
        "next_ranked": _next_ranked(conn, pick["ticker"] if pick else None),
        "remaining_daily_net": round(remaining_net, 2),
        "block_new_longs": summary.block_new_longs,
        "risk": risk_status,
        "portfolio_risk": risk_decision_to_dict(portfolio_risk),
        "pick_risk": risk_decision_to_dict(pick_risk) if pick_risk else None,
        "strategy": {
            "daily_net_target": daily_target,
            "stop_pct": STOP_PCT,
            "entry_delay_minutes": ENTRY_DELAY_MINUTES,
            "entry_window_et": ENTRY_WINDOW_ET,
        },
        "quote_snapshots": quote_snapshot_status,
        "market_activity": market_activity,
        "confirmations": confirmations,
        "phase1b": phase1b,
        "exceptional_trade": exceptional,
    }


def _next_ranked(conn: sqlite3.Connection, after_ticker: str | None) -> list[dict]:
    ranked = build_ranked_candidates(conn, period_days=14, require_opportunity_floor=True)["ranked"]
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
