"""CIO managing agent — rule-based dashboard summary (Phase 5, no Claude)."""

from __future__ import annotations

import sqlite3

from investment_agent.account import build_dashboard_summary, summary_to_dict
from investment_agent.learning import generate_learning_report
from investment_agent.monitor import list_active_alerts
from investment_agent.stock_team import list_queue, screen_candidates


def build_cio_summary(conn: sqlite3.Connection) -> dict:
    """Aggregate sub-agent outputs into a single CIO panel (rule-based until Claude)."""
    dash = build_dashboard_summary(conn)
    dash_dict = summary_to_dict(dash)
    learning = generate_learning_report(conn)
    queue = list_queue(conn)
    alerts = list_active_alerts(conn)
    candidates = screen_candidates(conn)

    state_counts: dict[str, int] = {}
    for item in queue:
        state_counts[item["state"]] = state_counts.get(item["state"], 0) + 1

    in_trade = state_counts.get("in_trade", 0) + state_counts.get("eod", 0)
    action_items: list[str] = []

    if dash.block_new_longs:
        action_items.append("Regime blocks new longs — manage open positions only.")
    elif candidates:
        action_items.append(
            f"{len(candidates)} screener candidate(s) — sync queue if you want fresh ideas."
        )

    if alerts:
        action_items.append(f"{len(alerts)} active price alert(s) — review intraday panel.")
    if in_trade:
        action_items.append(f"{in_trade} position(s) in trade/EOD — confirm flat by close or log exit.")
    if learning["eod_open_positions"]:
        action_items.append("Learning flagged open positions near EOD — verify overnight hold policy.")
    if dash.monthly_realized_net <= 0 and dash.total_fees_paid > 0:
        action_items.append(
            f"Month net ${dash.monthly_realized_net:.2f} after ${dash.total_fees_paid:.2f} fees — "
            "fees matter at $7/$7; aim for +1.13% targets."
        )
    if not action_items:
        action_items.append("No urgent actions — run ingest + monitor to stay current.")

    headline_parts: list[str] = []
    if dash.block_new_longs:
        headline_parts.append("Caution: triple-index down")
    else:
        headline_parts.append("Regime OK for new longs")
    headline_parts.append(f"${dash.tradable_cash:,.0f} tradable")
    headline_parts.append(f"goal {dash.goal_pct:.4f}%")
    headline = " · ".join(headline_parts)

    narrative_parts = [
        f"CIO summary (rule-based, no Claude). {headline}.",
        dash.market_brief.split(".")[0] + "." if dash.market_brief else "",
        f"Queue: {len(queue)} item(s)"
        + (f" ({in_trade} live)" if in_trade else "")
        + f"; {len(alerts)} alert(s); month P&L ${dash.monthly_realized_net:+.2f}.",
    ]
    if learning["highlights"]:
        narrative_parts.append(learning["highlights"][0])
    narrative = " ".join(p for p in narrative_parts if p)

    return {
        "headline": headline,
        "narrative": narrative,
        "action_items": action_items[:6],
        "sub_agents": {
            "research": dash.market_brief.split(". Rule-based")[0],
            "regime": (
                dash.regime["summary"]
                if dash.regime
                else "No regime data — run ingest."
            ),
            "stock_team": f"{len(candidates)} qualified candidate(s) on screener",
            "monitor": f"{len(alerts)} active alert(s); {in_trade} in-trade queue item(s)",
            "learning": (
                learning["highlights"][0]
                if learning["highlights"]
                else "No journal activity to analyze yet."
            ),
        },
        "queue_summary": {
            "total": len(queue),
            "by_state": state_counts,
        },
        "goal_pct": dash.goal_pct,
        "tradable_cash": dash.tradable_cash,
        "monthly_realized_net": dash.monthly_realized_net,
        "block_new_longs": dash.block_new_longs,
        "claude_ready": False,
        "dashboard": dash_dict,
    }
