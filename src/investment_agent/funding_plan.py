"""Operator funding & RH transition plan (evidence-gated dates).

Displayed on Account. Dates are earliest sketches — deposits stay gated
(never automatic). December 2026 paper runs at the $15k live seed size;
RH CASH live earliest 2027-01-04 after Dec 30/60/90 review pass.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from investment_agent.execution.ops_audit import get_ledger_source
from investment_agent.execution.paper_ledger import (
    ACCOUNT_GATE,
    PAPER_STARTING_CASH,
    ensure_paper_accounts,
    get_paper_balance,
    paper_scoreboard,
)
from investment_agent.trading_day import today_et_str

# Paper experiment notional (sized to match Jan 2027 live seed)
PAPER_NOTIONAL = PAPER_STARTING_CASH  # 15_000
LIVE_SEED = 15_000.0
TARGET_INVESTED = 15_000.0  # fresh $15k seed (not a paper roll)

# Capital Builder band while on paper / early live
PAPER_PHASE_START = 15_000.0
PAPER_PHASE_TARGET = 30_000.0

RH_LIVE_DATE = "2027-01-04"
PAPER_REVIEW_DATE = "2026-12-31"  # Dec 30/60/90 review window close


def funding_plan_rows(*, as_of: str | None = None) -> list[dict[str, Any]]:
    """Static schedule: Oct–Nov history → Dec $15k paper → Jan 4 2027 RH $15k."""
    today = as_of or today_et_str()
    rows = [
        {
            "id": "paper_start",
            "stage": "Paper book start (Oct–Nov history)",
            "date": "2026-10-20",
            "cash_in": 0.0,
            "invested_after": 0.0,
            "paper_notional": 5_000.0,
            "status_hint": "active" if today >= "2026-10-20" else "upcoming",
            "gate": "Internal paper ledger — keep all Oct–Nov fills/logs",
        },
        {
            "id": "paper_scale_15k",
            "stage": "Scale paper books to $15k (Dec sizing)",
            "date": "2026-12-01",
            "cash_in": 0.0,
            "invested_after": 0.0,
            "paper_notional": PAPER_NOTIONAL,
            "status_hint": "upcoming",
            "gate": (
                "Top-up credit only — preserves fills · "
                "~1.50% net target (~$225/trade) · mode stays paper"
            ),
        },
        {
            "id": "paper_review",
            "stage": "Dec 30/60/90 paper review",
            "date": PAPER_REVIEW_DATE,
            "cash_in": 0.0,
            "invested_after": 0.0,
            "paper_notional": PAPER_NOTIONAL,
            "status_hint": "upcoming",
            "gate": (
                "Pass §5.2 at $15k sizing (≥30 fills, +expectancy, "
                "beat control, DD≤10%) before any live seed"
            ),
        },
        {
            "id": "rh_live_1",
            "stage": "Robinhood live — $15k CASH seed",
            "date": RH_LIVE_DATE,
            "cash_in": LIVE_SEED,
            "invested_after": LIVE_SEED,
            "paper_notional": None,
            "status_hint": "gated",
            "gate": (
                "After Dec review pass · fresh $15k seed (not paper roll) · "
                "CASH/unlevered · same-day EOD flatten · "
                "ledger_source→robinhood · hard −10% stop — not automatic"
            ),
        },
    ]
    for r in rows:
        d = r["date"]
        if r["status_hint"] == "gated":
            continue
        if today > d and r["id"] == "paper_start":
            r["status_hint"] = "active"
        elif today >= d and r["id"] in {"paper_scale_15k", "paper_review"}:
            r["status_hint"] = "due" if r["id"] == "paper_review" else "active"
        elif today < d:
            r["status_hint"] = "upcoming"
    return rows


def build_funding_plan_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    ensure_paper_accounts(conn, starting_cash=PAPER_STARTING_CASH)
    bal = get_paper_balance(conn, ACCOUNT_GATE)
    source = get_ledger_source(conn)
    sb = paper_scoreboard(conn)
    today = today_et_str()
    rows = funding_plan_rows(as_of=today)

    paper_pass = bool(sb.get("paper_pass"))
    for r in rows:
        if r["id"] == "paper_review":
            r["status_hint"] = (
                "passed" if paper_pass else ("due" if today >= r["date"] else "upcoming")
            )
        if r["id"].startswith("rh_"):
            r["status_hint"] = "eligible" if paper_pass else "gated"

    next_funding = next(
        (
            r
            for r in rows
            if r["status_hint"] in {"gated", "eligible", "due", "upcoming"}
            and r["cash_in"] > 0
        ),
        None,
    )
    rh_row = next((r for r in rows if r["id"] == "rh_live_1"), None)

    return {
        "ok": True,
        "as_of_et": today,
        "ledger_source": source,
        "paper_starting_cash": PAPER_STARTING_CASH,
        "paper_equity": float(bal["equity"]),
        "paper_settled": float(bal["settled_cash"]),
        "paper_unsettled": float(bal["unsettled_cash"]),
        "phase_label": f"${PAPER_PHASE_START:,.0f} → ${PAPER_PHASE_TARGET:,.0f}",
        "phase_start": PAPER_PHASE_START,
        "phase_target": PAPER_PHASE_TARGET,
        "rh_transition": {
            "earliest_date": rh_row["date"] if rh_row else RH_LIVE_DATE,
            "amount": LIVE_SEED,
            "mode": "CASH / unlevered",
            "gate": rh_row["gate"] if rh_row else "",
            "ready": paper_pass,
        },
        "next_funding": next_funding,
        "scoreboard": {
            "paper_pass": paper_pass,
            "fills": sb.get("arms", {}).get(ACCOUNT_GATE, {}).get("fills", 0),
        },
        "stages": rows,
        "notes": (
            "Dec 2026 paper at $15k sizing (~$225 net/trade · 1.50%). "
            f"RH CASH live earliest {RH_LIVE_DATE} after Dec 30/60/90 review pass — "
            "fresh $15k seed, not a paper roll. Mode stays paper until that written go. "
            "Same-day EOD flatten on live. Deposits stay evidence-gated — never automatic."
        ),
    }
