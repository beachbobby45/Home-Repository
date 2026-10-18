"""Operator funding & RH transition plan (evidence-gated dates).

Displayed on Account. Dates are earliest sketches spaced ~30 trading
sessions apart — deposits stay gated (never automatic).
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

# Paper experiment notional (not RH cash until live deposit)
PAPER_NOTIONAL = PAPER_STARTING_CASH  # 5_000
LIVE_TRANCHE = 5_000.0
TARGET_INVESTED = 20_000.0

# Capital Builder band while on paper / early live
PAPER_PHASE_START = 5_000.0
PAPER_PHASE_TARGET = 20_000.0  # four × $5k invested

# Cadence assumption: ~30 trading sessions ≈ ~6 calendar weeks
# (≤5 sessions/wk when markets open; skips weekends + US holidays).
# From RH Deposit #1 on 2026-12-01:
#   #2 ≈ 2027-01-13, #3 ≈ 2027-02-25, #4 ≈ 2027-04-09.


def funding_plan_rows(*, as_of: str | None = None) -> list[dict[str, Any]]:
    """Static schedule: Oct–Nov paper → Dec 1 RH CASH $5k → +$5k ~every 30 sessions."""
    today = as_of or today_et_str()
    rows = [
        {
            "id": "paper_start",
            "stage": "Paper book start",
            "date": "2026-10-20",
            "cash_in": 0.0,
            "invested_after": 0.0,
            "paper_notional": PAPER_NOTIONAL,
            "status_hint": "active" if today >= "2026-10-20" else "upcoming",
            "gate": "Internal $5k paper ledger — no RH funds",
        },
        {
            "id": "paper_review",
            "stage": "Paper window review",
            "date": "2026-11-28",
            "cash_in": 0.0,
            "invested_after": 0.0,
            "paper_notional": PAPER_NOTIONAL,
            "status_hint": "upcoming",
            "gate": "Pass §5.2 (≥30 fills, +expectancy, beat control, DD≤10%)",
        },
        {
            "id": "rh_live_1",
            "stage": "Robinhood live — Deposit #1 (CASH)",
            "date": "2026-12-01",
            "cash_in": LIVE_TRANCHE,
            "invested_after": LIVE_TRANCHE,
            "paper_notional": None,
            "status_hint": "gated",
            "gate": (
                "After Oct–Nov paper pass · CASH/unlevered · "
                "ledger_source→robinhood · hard −10% stop — not automatic"
            ),
        },
        {
            "id": "deposit_2",
            "stage": "Deposit #2",
            "date": "2027-01-13",
            "cash_in": LIVE_TRANCHE,
            "invested_after": 10_000.0,
            "paper_notional": None,
            "status_hint": "gated",
            "gate": (
                "~30 sessions after #1 (earliest sketch) · "
                "evidence + written go — not automatic"
            ),
        },
        {
            "id": "deposit_3",
            "stage": "Deposit #3",
            "date": "2027-02-25",
            "cash_in": LIVE_TRANCHE,
            "invested_after": 15_000.0,
            "paper_notional": None,
            "status_hint": "gated",
            "gate": (
                "~30 sessions after #2 (earliest sketch) · "
                "expectancy still positive; DD within limits; written go"
            ),
        },
        {
            "id": "deposit_4",
            "stage": "Deposit #4 (cap $20k in)",
            "date": "2027-04-09",
            "cash_in": LIVE_TRANCHE,
            "invested_after": TARGET_INVESTED,
            "paper_notional": None,
            "status_hint": "gated",
            "gate": (
                "~30 sessions after #3 (earliest sketch) → $20k invested · "
                "same evidence bar; optional — skip if edge absent"
            ),
        },
    ]
    for r in rows:
        d = r["date"]
        if r["status_hint"] == "gated":
            continue
        if today > d and r["id"] == "paper_start":
            r["status_hint"] = "active"
        elif today >= d and r["id"] == "paper_review":
            r["status_hint"] = "due"
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

    # Mark RH transition / deposits still gated until paper_pass
    paper_pass = bool(sb.get("paper_pass"))
    for r in rows:
        if r["id"] == "paper_review":
            r["status_hint"] = "passed" if paper_pass else ("due" if today >= r["date"] else "upcoming")
        if r["id"].startswith("rh_") or r["id"].startswith("deposit_"):
            r["status_hint"] = "eligible" if paper_pass and r["id"] == "rh_live_1" else "gated"

    next_funding = next(
        (r for r in rows if r["status_hint"] in {"gated", "eligible", "due", "upcoming"} and r["cash_in"] > 0),
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
        "phase_label": f"${PAPER_PHASE_START:,.0f} → ${PAPER_PHASE_TARGET:,.0f} invested",
        "phase_start": PAPER_PHASE_START,
        "phase_target": PAPER_PHASE_TARGET,
        "rh_transition": {
            "earliest_date": rh_row["date"] if rh_row else "2026-12-01",
            "amount": LIVE_TRANCHE,
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
            "Earliest sketches: RH live CASH $5k on 2026-12-01 after paper pass, "
            "then +$5k every ~30 trading sessions (2027-01-13 → 2027-02-25 → 2027-04-09) "
            "to $20k invested. Deposits stay evidence-gated — never automatic. "
            "Until RH connects, Account balance is the paper book (starts $5,000)."
        ),
    }
