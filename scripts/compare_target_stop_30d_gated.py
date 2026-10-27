#!/usr/bin/env python3
"""Gated 30d #1 pullback backtest — closer to live dashboard/paper rules.

Backtest only (no dashboard changes). Same pullback + 5m fill proof as
compare_target_stop_30d.py, but reports P&L on filtered day sets:

  1) ALL days          — unrestricted counterfactual (prior study)
  2) MA allow_trade    — market-activity gate said TRADE
  3) PAPER eligible    — gate_approved paper log not a hard skip / no-pick fail
  4) STRICT            — (2) AND (3) when paper log exists; else (2) only

Also prints a live-alignment column: what paper actually logged that day.

Usage (Mac):
  cd ~/Home-Repository
  git fetch origin cursor/compare-target-stop-backtest-cd1d
  git checkout cursor/compare-target-stop-backtest-cd1d
  git pull
  PYTHONPATH=src .venv/bin/python3 scripts/compare_target_stop_30d_gated.py --days 30 --deploy 5000
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from investment_agent.db import connect, init_db  # noqa: E402
from investment_agent.execution.paper_ledger import ACCOUNT_GATE  # noqa: E402
from investment_agent.period_screener import list_trading_dates  # noqa: E402
from investment_agent.strategy import STOP_PCT  # noqa: E402

from compare_target_stop_30d import _run_arm, _summarize  # noqa: E402

# Paper statuses that mean "live process did not have a tradable armed pick"
_PAPER_NO_PICK = frozenset(
    {
        "waiting_signal",
        "no_signal",
        "propose_failed",
    }
)
_PAPER_HARD_SKIP = frozenset(
    {
        "skipped_gate",
        "skipped_cap",
        "skipped_cash",
    }
)


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row is not None


def _paper_gate_by_day(
    conn: sqlite3.Connection, days: list[str]
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not _table_exists(conn, "paper_session_logs"):
        return out
    if not days:
        return out
    placeholders = ",".join("?" * len(days))
    rows = conn.execute(
        f"""
        SELECT session_date_et, ticker, status, scenario, allow_trade, ma_score, detail
        FROM paper_session_logs
        WHERE account_name = ?
          AND session_date_et IN ({placeholders})
        """,
        (ACCOUNT_GATE, *days),
    ).fetchall()
    for r in rows:
        out[str(r["session_date_et"])] = {
            "ticker": r["ticker"],
            "status": r["status"],
            "scenario": r["scenario"],
            "allow_trade": None
            if r["allow_trade"] is None
            else bool(r["allow_trade"]),
            "ma_score": r["ma_score"],
            "detail": (r["detail"] or "")[:80],
        }
    return out


def _annotate_live(
    rows: list[dict], paper_by_day: dict[str, dict]
) -> list[dict]:
    annotated: list[dict] = []
    for r in rows:
        day = r["session_date_et"]
        paper = paper_by_day.get(day)
        allow = r.get("allow_trade")
        ma_ok = allow is True
        ma_missing = allow is None

        paper_eligible: bool | None
        paper_label = "no_paper_log"
        if paper is None:
            paper_eligible = None
        else:
            st = (paper.get("status") or "").strip()
            sc = (paper.get("scenario") or "").strip()
            tkr = (paper.get("ticker") or "").strip()
            paper_label = f"{st}/{sc or '-'}"
            if st in _PAPER_HARD_SKIP:
                paper_eligible = False
            elif st in _PAPER_NO_PICK or sc in {"propose_failed", "no_top_pick"}:
                paper_eligible = False
            elif not tkr and st in _PAPER_NO_PICK | {"waiting_signal"}:
                paper_eligible = False
            else:
                # Has a ticker or a non-fail working status (armed/complete/etc.)
                paper_eligible = True

        if ma_missing and paper_eligible is None:
            strict_ok = False
            strict_reason = "no_ma_and_no_paper"
        elif ma_ok and paper_eligible is False:
            strict_ok = False
            strict_reason = "ma_yes_paper_blocked"
        elif ma_ok and paper_eligible is True:
            strict_ok = True
            strict_reason = "ma_yes_paper_ok"
        elif ma_ok and paper_eligible is None:
            # No paper log yet for that historical day — MA gate is best proxy
            strict_ok = True
            strict_reason = "ma_yes_no_paper_log"
        elif (allow is False) and paper_eligible is True:
            strict_ok = False
            strict_reason = "ma_no_but_paper_had_ticker"
        else:
            strict_ok = False
            strict_reason = "ma_blocked_or_unknown"

        annotated.append(
            {
                **r,
                "live_ma_allow": allow,
                "live_paper": paper,
                "live_paper_label": paper_label,
                "filter_ma_allow": ma_ok,
                "filter_paper_eligible": paper_eligible is True,
                "filter_strict": strict_ok,
                "strict_reason": strict_reason,
            }
        )
    return annotated


def _filter_rows(rows: list[dict], key: str) -> list[dict]:
    return [r for r in rows if r.get(key)]


def _print_summary_block(title: str, sum_a: dict, sum_b: dict, n_days: int) -> None:
    print()
    print(f"=== {title} (n={n_days} days) ===")
    print(f"  {'metric':<22} {'CURRENT':>12} {'PROPOSED':>12}")
    for label, key in [
        ("fills", "fills"),
        ("no fill by 11:30", "no_fill_by_1130"),
        ("target exits", "target_exits"),
        ("stop exits", "stop_exits"),
        ("eod exits", "eod_exits"),
        ("win rate on fills %", "win_rate_pct_on_fills"),
        ("avg win $", "avg_win"),
        ("avg loss $", "avg_loss"),
        ("net P&L $", "net_pnl"),
        ("ending capital $", "ending_capital"),
    ]:
        print(f"  {label:<22} {sum_a[key]!s:>12} {sum_b[key]!s:>12}")
    delta = sum_b["net_pnl"] - sum_a["net_pnl"]
    print(f"  Proposed − Current: ${delta:+,.2f}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gated compare: only days live MA/paper would allow"
    )
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--deploy", type=float, default=5_000.0)
    parser.add_argument("--current-target", type=float, default=75.0)
    parser.add_argument("--current-stop-pct", type=float, default=STOP_PCT)
    parser.add_argument("--proposed-target", type=float, default=55.0)
    parser.add_argument("--proposed-stop-pct", type=float, default=0.50)
    parser.add_argument("--fees", type=float, default=0.0)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    db_path = init_db(args.db)
    if not Path(db_path).is_file():
        print(f"ERROR: database not found at {db_path}")
        return 2

    conn = connect(db_path)
    try:
        trading_days = list_trading_dates(conn, count=args.days)
        if not trading_days:
            print("ERROR: no trading dates in ohlcv_daily")
            return 3

        print("=== GATED COMPARE (live-aligned filters) ===")
        print(f"DB: {db_path}")
        print(f"Days: {len(trading_days)} ({trading_days[0]} → {trading_days[-1]})")
        print(f"Deploy ${args.deploy:,.2f} | fees/side ${args.fees:.2f}")
        print(
            f"Arm A CURRENT  ${args.current_target:.0f} / {args.current_stop_pct:.2f}% stop"
        )
        print(
            f"Arm B PROPOSED ${args.proposed_target:.0f} / {args.proposed_stop_pct:.2f}% stop"
        )
        print()
        print("Filters:")
        print("  ALL         = every session (unrestricted counterfactual)")
        print("  MA_ALLOW    = market_activity allow_trade=True")
        print("  PAPER_OK    = gate_approved log not no-pick / hard skip")
        print("  STRICT      = MA_ALLOW, and PAPER_OK when a paper log exists")
        print()
        print("Replaying 5m bars (shared cache)…")

        bars_cache: dict = {}
        fee = float(args.fees)
        rows_a = _run_arm(
            conn,
            trading_days,
            deploy=float(args.deploy),
            bars_cache=bars_cache,
            lookback_days=args.lookback_days,
            net_target=float(args.current_target),
            stop_pct=float(args.current_stop_pct),
            buy_fee=fee,
            sell_fee=fee,
        )
        rows_b = _run_arm(
            conn,
            trading_days,
            deploy=float(args.deploy),
            bars_cache=bars_cache,
            lookback_days=args.lookback_days,
            net_target=float(args.proposed_target),
            stop_pct=float(args.proposed_stop_pct),
            buy_fee=fee,
            sell_fee=fee,
        )

        paper_by_day = _paper_gate_by_day(conn, trading_days)
        ann_a = _annotate_live(rows_a, paper_by_day)
        # Copy live annotations onto B by date
        live_by_day = {r["session_date_et"]: r for r in ann_a}
        ann_b = []
        for r in rows_b:
            live = live_by_day[r["session_date_et"]]
            ann_b.append(
                {
                    **r,
                    "live_ma_allow": live["live_ma_allow"],
                    "live_paper": live["live_paper"],
                    "live_paper_label": live["live_paper_label"],
                    "filter_ma_allow": live["filter_ma_allow"],
                    "filter_paper_eligible": live["filter_paper_eligible"],
                    "filter_strict": live["filter_strict"],
                    "strict_reason": live["strict_reason"],
                }
            )

        print()
        print(
            f"{'DATE':<12} {'TCKR':<6} {'MA':>3} {'PAPER':<22} {'STRICT':<5} "
            f"{'A_NET':>8} {'B_NET':>8} {'A_SCEN':<22}"
        )
        for a, b in zip(ann_a, ann_b):
            ma = a.get("live_ma_allow")
            ma_s = "Y" if ma is True else ("N" if ma is False else "—")
            a_net = (
                f"{float(a['net_pnl']):.2f}"
                if a.get("counts_toward_pnl") and a.get("net_pnl") is not None
                else "EXCL"
            )
            b_net = (
                f"{float(b['net_pnl']):.2f}"
                if b.get("counts_toward_pnl") and b.get("net_pnl") is not None
                else "EXCL"
            )
            print(
                f"{a['session_date_et']:<12} {(a.get('ticker') or '—'):<6} "
                f"{ma_s:>3} {a['live_paper_label']:<22} "
                f"{('Y' if a['filter_strict'] else 'N'):<5} "
                f"{a_net:>8} {b_net:>8} {(a.get('scenario') or '—'):<22}"
            )

        starting = float(args.deploy)
        views = [
            ("ALL (unrestricted)", ann_a, ann_b, None),
            ("MA_ALLOW only", ann_a, ann_b, "filter_ma_allow"),
            ("PAPER_OK only", ann_a, ann_b, "filter_paper_eligible"),
            ("STRICT (live-aligned)", ann_a, ann_b, "filter_strict"),
        ]

        view_payload = {}
        for title, aa, bb, key in views:
            fa = aa if key is None else _filter_rows(aa, key)
            fb = bb if key is None else _filter_rows(bb, key)
            # Keep only dates present in both (same set)
            dates = {r["session_date_et"] for r in fa}
            fb = [r for r in fb if r["session_date_et"] in dates]
            sa = _summarize(fa, starting=starting)
            sb = _summarize(fb, starting=starting)
            _print_summary_block(title, sa, sb, len(fa))
            view_payload[title] = {
                "n_days": len(fa),
                "current": sa,
                "proposed": sb,
                "delta_net_pnl": round(sb["net_pnl"] - sa["net_pnl"], 2),
            }

        n_ma = sum(1 for r in ann_a if r["filter_ma_allow"])
        n_paper = sum(1 for r in ann_a if r["filter_paper_eligible"])
        n_strict = sum(1 for r in ann_a if r["filter_strict"])
        n_paper_logs = sum(1 for r in ann_a if r.get("live_paper") is not None)
        print()
        print("=== FILTER COVERAGE ===")
        print(f"  Total days:              {len(ann_a)}")
        print(f"  MA allow_trade=True:     {n_ma}")
        print(f"  Paper logs present:      {n_paper_logs}")
        print(f"  Paper eligible:          {n_paper}")
        print(f"  STRICT live-aligned:     {n_strict}")
        print()
        print(
            "Note: STRICT is the closest dashboard-aligned slice. "
            "If paper logs are sparse historically, MA_ALLOW is the next-best proxy."
        )

        payload = {
            "deploy": args.deploy,
            "fees_per_side": args.fees,
            "views": view_payload,
            "days_annotated_current": ann_a,
            "days_annotated_proposed": ann_b,
        }
        out = args.json_out or (ROOT / "data" / "compare_target_stop_30d_gated.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2))
        print(f"\nWrote {out}")

        # Human-readable HTML beside the JSON
        try:
            from render_gated_backtest_html import render

            html_path = out.with_suffix(".html")
            html_path.write_text(render(payload))
            print(f"Wrote {html_path}")
            print(f"Open in browser: open {html_path}")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: HTML render skipped: {exc}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
