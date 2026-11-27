#!/usr/bin/env python3
"""Investor-style paper assessment from local agent.db (factual, no estimates).

Usage (Mac):
  cd ~/Home-Repository && python3 scripts/paper_investor_assessment.py
  cd ~/Home-Repository && python3 scripts/paper_investor_assessment.py --days 30,60
"""

from __future__ import annotations

import argparse
import sqlite3
import statistics
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
PRIMARY = "gate_approved"
SHADOW = "all_signals"

# Locked Target 1 / Nov-pace planning assumptions (docs/TARGET1_STRATEGY.md)
ASSUMPTION_WIN_PCT = 1.504  # % of equity per win (TYL+TTEK avg on $5k)
ASSUMPTION_WINS_PER_WEEK = 1.0
ASSUMPTION_LOSS_RATE = 0.0  # planning sheets assumed no losses
START_BASIS = 5_000.0


def _connect(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _window_start(asof: date, days: int) -> date:
    return asof - timedelta(days=days - 1)


def _fetch_sessions(
    conn: sqlite3.Connection,
    *,
    account: str,
    start: str,
    end: str,
) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT session_date_et, ticker, filled, entry_price, exit_price, shares,
               net_pnl, fill_ts, exit_ts, scenario, detail
        FROM paper_session_logs
        WHERE account_name = ?
          AND session_date_et >= ?
          AND session_date_et <= ?
        ORDER BY session_date_et, ticker
        """,
        (account, start, end),
    ).fetchall()


def _classify(row: sqlite3.Row) -> str:
    scen = (row["scenario"] or "").lower()
    filled = int(row["filled"] or 0) == 1
    pnl = float(row["net_pnl"] or 0.0)
    if filled and pnl > 0:
        return "win"
    if filled and pnl < 0:
        return "loss"
    if filled and pnl == 0:
        return "scratch"
    if "gate_blocked" in scen:
        return "gate_blocked"
    if "no_fill" in scen:
        return "no_fill"
    if "propose_failed" in scen:
        return "propose_failed"
    if "eod" in scen:
        return "eod_flat"
    return "other_flat"


def _summarize(rows: list[sqlite3.Row]) -> dict:
    classes = Counter(_classify(r) for r in rows)
    fills = [r for r in rows if int(r["filled"] or 0) == 1]
    pnls = [float(r["net_pnl"] or 0.0) for r in fills]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    sessions = sorted({r["session_date_et"] for r in rows})
    fill_days = sorted({r["session_date_et"] for r in fills})
    net = round(sum(float(r["net_pnl"] or 0.0) for r in rows), 2)
    fill_net = round(sum(pnls), 2) if pnls else 0.0
    return {
        "session_rows": len(rows),
        "unique_sessions": len(sessions),
        "fill_days": len(fill_days),
        "classes": dict(classes),
        "fills": len(fills),
        "wins": len(wins),
        "losses": len(losses),
        "scratches": classes.get("scratch", 0),
        "gate_blocked": classes.get("gate_blocked", 0),
        "no_fill": classes.get("no_fill", 0),
        "propose_failed": classes.get("propose_failed", 0),
        "other_flat": classes.get("other_flat", 0) + classes.get("eod_flat", 0),
        "gross_win": round(sum(wins), 2) if wins else 0.0,
        "gross_loss": round(sum(losses), 2) if losses else 0.0,
        "net": net,
        "fill_net": fill_net,
        "avg_win": round(statistics.mean(wins), 2) if wins else None,
        "avg_loss": round(statistics.mean(losses), 2) if losses else None,
        "win_rate_on_fills": round(100.0 * len(wins) / len(fills), 1) if fills else None,
        "expectancy_per_fill": round(fill_net / len(fills), 2) if fills else None,
        "expectancy_per_session_row": round(net / len(rows), 2) if rows else None,
        "pnls": pnls,
        "fills_detail": fills,
        "sessions": sessions,
    }


def _ma_breakdown(conn: sqlite3.Connection, start: str, end: str) -> dict | None:
    if not _table_exists(conn, "market_activity_evaluations"):
        return None
    rows = conn.execute(
        """
        SELECT session_date_et, score, band, allow_trade, summary
        FROM market_activity_evaluations
        WHERE session_date_et >= ? AND session_date_et <= ?
        ORDER BY session_date_et, captured_at
        """,
        (start, end),
    ).fetchall()
    if not rows:
        return None
    # last eval per session
    last: dict[str, sqlite3.Row] = {}
    for r in rows:
        last[r["session_date_et"]] = r
    bands = Counter((r["band"] or "unknown") for r in last.values())
    allow = sum(1 for r in last.values() if int(r["allow_trade"] or 0) == 1)
    scores = [float(r["score"]) for r in last.values() if r["score"] is not None]
    return {
        "sessions_with_ma": len(last),
        "allow_trade_days": allow,
        "block_trade_days": len(last) - allow,
        "bands": dict(bands),
        "avg_score": round(statistics.mean(scores), 1) if scores else None,
        "min_score": round(min(scores), 1) if scores else None,
        "max_score": round(max(scores), 1) if scores else None,
    }


def _fmt_money(n: float | None) -> str:
    if n is None:
        return "n/a"
    return f"${n:,.2f}"


def _fmt_pct(n: float | None) -> str:
    if n is None:
        return "n/a"
    return f"{n:.1f}%"


def _print_book(title: str, s: dict) -> None:
    print(f"\n### {title}")
    print(f"- Session rows: **{s['session_rows']}** across **{s['unique_sessions']}** unique dates")
    print(f"- Fills: **{s['fills']}** on **{s['fill_days']}** days "
          f"(W {s['wins']} / L {s['losses']} / scratch {s['scratches']})")
    print(f"- Win rate on fills: **{_fmt_pct(s['win_rate_on_fills'])}**")
    print(f"- Net P&L (all rows): **{_fmt_money(s['net'])}**  |  fill-only net: **{_fmt_money(s['fill_net'])}**")
    print(f"- Avg win: **{_fmt_money(s['avg_win'])}**  |  Avg loss: **{_fmt_money(s['avg_loss'])}**")
    print(f"- Expectancy / fill: **{_fmt_money(s['expectancy_per_fill'])}**  |  "
          f"/ session row: **{_fmt_money(s['expectancy_per_session_row'])}**")
    print(
        f"- Non-fills: gate_blocked **{s['gate_blocked']}**, no_fill **{s['no_fill']}**, "
        f"propose_failed **{s['propose_failed']}**, other_flat **{s['other_flat']}**"
    )
    if s["fills_detail"]:
        print("- Fills:")
        for r in s["fills_detail"]:
            print(
                f"  - {r['session_date_et']} {r['ticker']}: "
                f"{r['entry_price']} → {r['exit_price']} × {r['shares']}  "
                f"net={_fmt_money(float(r['net_pnl'] or 0))}  ({r['scenario']})"
            )


def _compare_assumptions(primary: dict, days: int, equity_now: float | None) -> None:
    print(f"\n### Target 1 / Nov-pace assumptions vs last {days}d (primary book)")
    print(
        f"- Planning assumption: **{ASSUMPTION_WINS_PER_WEEK:.1f} win/week**, "
        f"**{ASSUMPTION_WIN_PCT:.3f}%** equity per win, **0%** loss rate on filled days"
    )
    weeks = max(days / 7.0, 1e-9)
    wins_per_week = primary["wins"] / weeks
    print(f"- Observed wins/week (calendar): **{wins_per_week:.2f}** "
          f"({primary['wins']} wins / {days}d ≈ {weeks:.1f} weeks)")
    if primary["fills"]:
        loss_rate = 100.0 * primary["losses"] / primary["fills"]
        print(f"- Observed loss rate on fills: **{loss_rate:.1f}%** "
              f"(assumption was {ASSUMPTION_LOSS_RATE:.0f}%)")
    if primary["avg_win"] is not None and equity_now:
        pct = 100.0 * primary["avg_win"] / equity_now
        # also vs $5k basis used when wins were sized
        pct_basis = 100.0 * primary["avg_win"] / START_BASIS
        print(
            f"- Avg win vs $5k basis: **{pct_basis:.3f}%** "
            f"(assumption {ASSUMPTION_WIN_PCT:.3f}%); "
            f"vs current cash {_fmt_money(equity_now)}: **{pct:.3f}%**"
        )
    # Rough planned net if assumption held every week with no losses
    planned_weekly = START_BASIS * (ASSUMPTION_WIN_PCT / 100.0) * ASSUMPTION_WINS_PER_WEEK
    planned = planned_weekly * weeks
    print(
        f"- Naive planned net if Nov-pace held unbroken on $5k for {days}d: "
        f"**{_fmt_money(planned)}** vs actual primary net **{_fmt_money(primary['net'])}**"
    )


def _verdict(primary: dict, shadow: dict | None, days: int) -> None:
    print("\n## Verdict (fact-based)")
    fills = primary["fills"]
    net = primary["net"]
    exp = primary["expectancy_per_fill"]
    gates = primary["gate_blocked"]

    works = False
    reasons: list[str] = []
    caveats: list[str] = []

    if fills == 0:
        reasons.append(
            f"No primary fills in the last {days} days — cannot claim a working edge from fills."
        )
    else:
        if net > 0 and exp is not None and exp > 0:
            works = True
            reasons.append(
                f"Primary book is net positive (**{_fmt_money(net)}**) with positive "
                f"expectancy per fill (**{_fmt_money(exp)}**) over **{fills}** fills."
            )
        elif net <= 0:
            reasons.append(
                f"Primary book net is **{_fmt_money(net)}** over **{fills}** fills — "
                "not investor-ready as a profitable system in this window."
            )
        if primary["wins"] and primary["losses"]:
            if primary["avg_win"] and primary["avg_loss"]:
                rr = abs(primary["avg_win"] / primary["avg_loss"]) if primary["avg_loss"] else None
                if rr:
                    reasons.append(
                        f"Avg win/avg loss magnitude ≈ **{rr:.2f}×** "
                        f"({_fmt_money(primary['avg_win'])} vs {_fmt_money(primary['avg_loss'])})."
                    )
        if gates:
            reasons.append(
                f"Gate blocked **{gates}** session rows — risk filter is active in sample "
                "(capital preservation behavior is observable, not theoretical)."
            )

    if fills < 10:
        caveats.append(
            f"Only **{fills}** primary fills in {days}d — sample is **too small** for "
            "statistical confidence; treat as directional evidence, not proof."
        )
    if shadow and shadow["fills"] and primary["fills"] is not None:
        if shadow["net"] > primary["net"]:
            caveats.append(
                f"Shadow `all_signals` net (**{_fmt_money(shadow['net'])}**) exceeded primary "
                f"(**{_fmt_money(primary['net'])}**) in this window — gate may be skipping "
                "some winners (cost of risk control). Compare fill lists before changing rules."
            )
        elif shadow["net"] < primary["net"]:
            reasons.append(
                f"Primary outperformed shadow in this window "
                f"({_fmt_money(primary['net'])} vs {_fmt_money(shadow['net'])}) — "
                "gate filtering is not obviously destroying edge here."
            )

    label = "YES — provisional" if works else "NOT YET / NO"
    print(f"**Does the model work?** **{label}**")
    print("\n**Why (from this DB window):**")
    for r in reasons:
        print(f"- {r}")
    if caveats:
        print("\n**Caveats / what not to overclaim:**")
        for c in caveats:
            print(f"- {c}")


def _updates(primary_30: dict, primary_60: dict, shadow_30: dict | None) -> None:
    print("\n## What to update (only if facts support it)")
    updates: list[str] = []

    # Loss assumption broken?
    for label, s in (("30d", primary_30), ("60d", primary_60)):
        if s["losses"] > 0:
            updates.append(
                f"Replace Target 1 ‘no losses’ planning with observed fill loss rate "
                f"({s['losses']}/{s['fills']} = "
                f"{(100.0*s['losses']/s['fills']):.1f}% in {label}) when projecting."
            )
            break

    # Win frequency vs 1/week
    for label, s, days in (("30d", primary_30, 30), ("60d", primary_60, 60)):
        wpw = s["wins"] / (days / 7.0)
        if s["unique_sessions"] >= 5:
            updates.append(
                f"Recalibrate wins/week using measured **{wpw:.2f}** in {label} "
                f"(plan assumed {ASSUMPTION_WINS_PER_WEEK:.1f})."
            )
            break

    # Gate opportunity cost
    if shadow_30 and shadow_30["wins"] > primary_30["wins"]:
        updates.append(
            "Keep gate (risk control is evidenced) but log every shadow win on blocked days "
            "as a structured opportunity-cost review — do **not** loosen MA≥50 without a "
            "side-by-side blocked-day P&L study from this DB."
        )

    if primary_30["fills"] + primary_60["fills"] < 15:
        updates.append(
            "Do **not** change entry/stop/target parameters yet — fill count is below a "
            "minimum bar for parameter surgery. Continue paper through December for sample size."
        )

    if not updates:
        updates.append(
            "No parameter changes justified yet beyond tracking measured win frequency and "
            "loss rate into Target 1 projections."
        )

    # de-dupe while preserving order
    seen = set()
    for u in updates:
        if u in seen:
            continue
        seen.add(u)
        print(f"- {u}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Paper investor assessment from agent.db")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--days", default="30,60", help="Comma-separated lookbacks")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    db = args.db or (root / "data" / "agent.db")
    if not db.exists():
        raise SystemExit(f"Missing DB: {db}")

    day_list = [int(x.strip()) for x in args.days.split(",") if x.strip()]
    asof = datetime.now(ET).date()
    asof_s = asof.isoformat()

    conn = _connect(db)
    if not _table_exists(conn, "paper_session_logs"):
        raise SystemExit("paper_session_logs table not found")

    equity_now = None
    try:
        import sys

        sys.path.insert(0, str(root / "src"))
        from investment_agent.db import connect as ag_connect, init_db
        from investment_agent.account import build_dashboard_summary

        c2 = ag_connect(init_db(db))
        try:
            equity_now = float(build_dashboard_summary(c2).tradable_cash or 0)
        finally:
            c2.close()
    except Exception:
        # fallback: infer from paper if possible
        equity_now = None

    print("=" * 72)
    print("PAPER TRADING — INVESTOR ASSESSMENT (FACTUAL FROM agent.db)")
    print(f"As of: {datetime.now(ET).strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"DB: {db}")
    if equity_now is not None:
        print(f"Tradable cash (dashboard): {_fmt_money(equity_now)}")
        print(f"Vs $5,000 basis: {_fmt_money(equity_now - START_BASIS)} "
              f"({100.0 * (equity_now - START_BASIS) / START_BASIS:+.2f}%)")
    print("=" * 72)

    print(
        "\n## Scope\n"
        "- Books: **gate_approved** (primary) and **all_signals** (shadow)\n"
        "- Source: `paper_session_logs` (+ market_activity_evaluations if present)\n"
        "- No forward estimates; all figures below are counted from this database."
    )

    summaries: dict[int, dict] = {}
    shadows: dict[int, dict] = {}

    for days in day_list:
        start = _window_start(asof, days).isoformat()
        print("\n" + "-" * 72)
        print(f"## Last {days} calendar days  ({start} → {asof_s})")
        print("-" * 72)

        primary_rows = _fetch_sessions(conn, account=PRIMARY, start=start, end=asof_s)
        shadow_rows = _fetch_sessions(conn, account=SHADOW, start=start, end=asof_s)
        primary = _summarize(primary_rows)
        shadow = _summarize(shadow_rows)
        summaries[days] = primary
        shadows[days] = shadow

        _print_book(f"Primary `{PRIMARY}`", primary)
        _print_book(f"Shadow `{SHADOW}`", shadow)

        ma = _ma_breakdown(conn, start, asof_s)
        if ma:
            print("\n### Market activity (last eval / session)")
            print(f"- Sessions with MA rows: **{ma['sessions_with_ma']}**")
            print(
                f"- Allow-trade days: **{ma['allow_trade_days']}**  |  "
                f"Block days: **{ma['block_trade_days']}**"
            )
            print(f"- Score avg/min/max: **{ma['avg_score']}** / **{ma['min_score']}** / **{ma['max_score']}**")
            print(f"- Bands: {ma['bands']}")
        else:
            print("\n### Market activity")
            print("- No `market_activity_evaluations` rows in window (or table missing).")

        _compare_assumptions(primary, days, equity_now)

    # Prefer 30d for headline verdict, mention 60d
    p30 = summaries.get(30) or next(iter(summaries.values()))
    p60 = summaries.get(60) or p30
    s30 = shadows.get(30)

    print("\n" + "=" * 72)
    _verdict(p30, s30, 30 if 30 in summaries else day_list[0])
    if 60 in summaries and 30 in summaries:
        print(
            f"\n**60d cross-check (primary):** net **{_fmt_money(p60['net'])}**, "
            f"fills **{p60['fills']}**, W/L **{p60['wins']}/{p60['losses']}**, "
            f"expectancy/fill **{_fmt_money(p60['expectancy_per_fill'])}**."
        )

    _updates(p30, p60, s30)

    print("\n## Methods note for investors")
    print(
        "- Paper simulation uses historical/intraday bars with declared scenarios "
        "(`exit_target`, `exit_stop`, `gate_blocked`, `no_fill_by_1130`, etc.).\n"
        "- This is **not** live broker fills; slippage/queue risk can differ.\n"
        "- Day gate (MA band / allow_trade) is part of the product — primary book "
        "skips when `allow_trade=false`.\n"
        "- Presentation claim discipline: state sample size, net, win/loss, and "
        "gate activity before any projection."
    )
    print("\nDone.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
