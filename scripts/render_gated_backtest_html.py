#!/usr/bin/env python3
"""Render compare_target_stop_30d_gated.json → a readable HTML report."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


def _esc(v: object) -> str:
    return html.escape("" if v is None else str(v))


def _money(v: object) -> str:
    try:
        n = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "—"
    sign = "+" if n > 0 else ""
    return f"{sign}${n:,.2f}"


def _pct(v: object) -> str:
    try:
        return f"{float(v):.1f}%"  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "—"


def _ma_badge(allow: object) -> str:
    if allow is True:
        return '<span class="badge ok">TRADE</span>'
    if allow is False:
        return '<span class="badge no">NO TRADE</span>'
    return '<span class="badge mute">—</span>'


def _strict_badge(ok: object) -> str:
    return (
        '<span class="badge ok">YES</span>'
        if ok
        else '<span class="badge no">NO</span>'
    )


def _scenario_class(scen: object) -> str:
    s = str(scen or "")
    if "target" in s:
        return "tgt"
    if "stop" in s:
        return "stp"
    if "no_fill" in s:
        return "nf"
    if "eod" in s:
        return "eod"
    return ""


def render(payload: dict) -> str:
    views = payload.get("views") or {}
    days = payload.get("days_annotated_current") or []
    deploy = payload.get("deploy", 5000)
    fees = payload.get("fees_per_side", 0)

    # Normalize view keys if present
    view_order = [
        ("ALL (unrestricted)", "Unrestricted counterfactual — every #1 day"),
        ("MA_ALLOW only", "Only days market activity said TRADE"),
        ("PAPER_OK only", "Only days paper gate_approved was eligible"),
        ("STRICT (live-aligned)", "Closest to dashboard — MA TRADE + paper OK when logged"),
    ]

    cards = []
    for key, blurb in view_order:
        block = views.get(key) or {}
        cur = block.get("current") or {}
        prop = block.get("proposed") or {}
        n = block.get("n_days", 0)
        delta = block.get("delta_net_pnl", 0)
        delta_cls = "pos" if float(delta or 0) > 0 else ("neg" if float(delta or 0) < 0 else "neu")
        cards.append(
            f"""
            <article class="card">
              <h3>{_esc(key)}</h3>
              <p class="blurb">{_esc(blurb)}</p>
              <p class="n">Days in slice: <strong>{_esc(n)}</strong></p>
              <table class="mini">
                <thead><tr><th></th><th>Current<br>$75 / 0.75%</th><th>Proposed<br>$55 / 0.50%</th></tr></thead>
                <tbody>
                  <tr><td>Fills</td><td>{_esc(cur.get('fills'))}</td><td>{_esc(prop.get('fills'))}</td></tr>
                  <tr><td>No fill by 11:30</td><td>{_esc(cur.get('no_fill_by_1130'))}</td><td>{_esc(prop.get('no_fill_by_1130'))}</td></tr>
                  <tr><td>Target exits</td><td>{_esc(cur.get('target_exits'))}</td><td>{_esc(prop.get('target_exits'))}</td></tr>
                  <tr><td>Stop exits</td><td>{_esc(cur.get('stop_exits'))}</td><td>{_esc(prop.get('stop_exits'))}</td></tr>
                  <tr><td>Win rate</td><td>{_pct(cur.get('win_rate_pct_on_fills'))}</td><td>{_pct(prop.get('win_rate_pct_on_fills'))}</td></tr>
                  <tr><td>Avg win</td><td>{_money(cur.get('avg_win'))}</td><td>{_money(prop.get('avg_win'))}</td></tr>
                  <tr><td>Avg loss</td><td>{_money(cur.get('avg_loss'))}</td><td>{_money(prop.get('avg_loss'))}</td></tr>
                  <tr class="emph"><td>Net P&amp;L</td><td>{_money(cur.get('net_pnl'))}</td><td>{_money(prop.get('net_pnl'))}</td></tr>
                </tbody>
              </table>
              <p class="delta {delta_cls}">Proposed − Current: {_money(delta)}</p>
            </article>
            """
        )

    # Coverage
    n_total = len(days)
    n_ma = sum(1 for d in days if d.get("filter_ma_allow"))
    n_paper_logs = sum(1 for d in days if d.get("live_paper") is not None)
    n_paper_ok = sum(1 for d in days if d.get("filter_paper_eligible"))
    n_strict = sum(1 for d in days if d.get("filter_strict"))

    day_rows = []
    for d in days:
        scen = d.get("scenario") or "—"
        net = d.get("net_pnl")
        net_s = _money(net) if d.get("counts_toward_pnl") and net is not None else "EXCL"
        paper = d.get("live_paper_label") or "no_paper_log"
        day_rows.append(
            f"""
            <tr>
              <td>{_esc(d.get('session_date_et'))}</td>
              <td class="ticker">{_esc(d.get('ticker') or '—')}</td>
              <td>{_ma_badge(d.get('live_ma_allow'))}</td>
              <td class="paper">{_esc(paper)}</td>
              <td>{_strict_badge(d.get('filter_strict'))}</td>
              <td class="scen {_scenario_class(scen)}">{_esc(scen)}</td>
              <td class="num">{net_s}</td>
            </tr>
            """
        )

    first = days[0].get("session_date_et") if days else "—"
    last = days[-1].get("session_date_et") if days else "—"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Gated backtest — live-aligned vs unrestricted</title>
<style>
  :root {{
    --bg: #f6f4ef;
    --ink: #1c1a16;
    --muted: #5c574e;
    --card: #fffdf8;
    --line: #ddd6c8;
    --ok: #1f6b3a;
    --ok-bg: #e5f3ea;
    --no: #8a2e2e;
    --no-bg: #f8e8e8;
    --mute-bg: #eceae4;
    --accent: #245b6b;
    --pos: #1f6b3a;
    --neg: #8a2e2e;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Source Serif 4", "Iowan Old Style", Georgia, serif;
    color: var(--ink);
    background:
      radial-gradient(1200px 500px at 10% -10%, #e7eef0 0%, transparent 55%),
      radial-gradient(900px 400px at 100% 0%, #f0e8dc 0%, transparent 50%),
      var(--bg);
    line-height: 1.45;
  }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }}
  h1 {{ font-size: 1.85rem; margin: 0 0 8px; letter-spacing: -0.02em; }}
  h2 {{ font-size: 1.25rem; margin: 36px 0 12px; color: var(--accent); }}
  h3 {{ font-size: 1.05rem; margin: 0 0 6px; }}
  .sub {{ color: var(--muted); margin: 0 0 24px; max-width: 62ch; }}
  .callout {{
    background: var(--card);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    padding: 14px 16px;
    margin: 0 0 28px;
  }}
  .callout strong {{ color: var(--accent); }}
  .meta {{
    display: flex; flex-wrap: wrap; gap: 10px 18px;
    color: var(--muted); font-size: 0.95rem; margin-bottom: 20px;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 14px;
    margin-bottom: 8px;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--line);
    padding: 14px 14px 10px;
  }}
  .blurb {{ color: var(--muted); font-size: 0.92rem; margin: 0 0 10px; }}
  .n {{ margin: 0 0 10px; font-size: 0.92rem; }}
  table.mini {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  table.mini th, table.mini td {{
    border-bottom: 1px solid var(--line);
    padding: 5px 4px;
    text-align: right;
  }}
  table.mini th:first-child, table.mini td:first-child {{ text-align: left; }}
  table.mini th {{ color: var(--muted); font-weight: 600; font-size: 0.78rem; }}
  tr.emph td {{ font-weight: 700; }}
  .delta {{ margin: 10px 0 0; font-weight: 600; }}
  .delta.pos {{ color: var(--pos); }}
  .delta.neg {{ color: var(--neg); }}
  .delta.neu {{ color: var(--muted); }}
  .cov {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    margin: 12px 0 28px;
  }}
  .cov div {{
    background: var(--card);
    border: 1px solid var(--line);
    padding: 12px;
  }}
  .cov .k {{ color: var(--muted); font-size: 0.8rem; }}
  .cov .v {{ font-size: 1.4rem; font-weight: 700; }}
  .wrap {{ overflow-x: auto; border: 1px solid var(--line); background: var(--card); }}
  table.days {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  table.days th, table.days td {{
    padding: 8px 10px;
    border-bottom: 1px solid var(--line);
    text-align: left;
    white-space: nowrap;
  }}
  table.days th {{
    background: #f0ebe3;
    position: sticky; top: 0;
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  table.days tr:nth-child(even) td {{ background: #faf7f1; }}
  .ticker {{ font-weight: 700; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .paper {{ color: var(--muted); max-width: 220px; overflow: hidden; text-overflow: ellipsis; }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
  }}
  .badge.ok {{ background: var(--ok-bg); color: var(--ok); }}
  .badge.no {{ background: var(--no-bg); color: var(--no); }}
  .badge.mute {{ background: var(--mute-bg); color: var(--muted); }}
  .scen.tgt {{ color: var(--ok); }}
  .scen.stp {{ color: var(--no); }}
  .scen.nf {{ color: var(--muted); }}
  .scen.eod {{ color: #6a5420; }}
  footer {{ margin-top: 28px; color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
<main>
  <h1>Gated backtest report</h1>
  <p class="sub">
    Same #1 pullback simulation as before, sliced by whether the <em>live</em> system
    would have allowed a trade. This is why the dashboard can look flat while an
    unrestricted backtest shows profit.
  </p>

  <div class="callout">
    <strong>Takeaway:</strong>
    Unrestricted “always try #1” showed about <strong>+$425</strong> (current rules).
    Live-aligned slices (MA TRADE / STRICT) had <strong>1 day</strong> and
    <strong>$0</strong> — matching a quiet dashboard. Target $55 / stop 0.50% did not
    help on the live-aligned sample.
  </div>

  <div class="meta">
    <span>Window: <strong>{_esc(first)} → {_esc(last)}</strong></span>
    <span>Deploy: <strong>${_esc(f"{float(deploy):,.0f}")}</strong></span>
    <span>Fees/side: <strong>${_esc(fees)}</strong> (RH-like)</span>
    <span>Arms: <strong>$75 / 0.75%</strong> vs <strong>$55 / 0.50%</strong></span>
  </div>

  <h2>Filter coverage</h2>
  <div class="cov">
    <div><div class="k">Total days</div><div class="v">{n_total}</div></div>
    <div><div class="k">MA TRADE</div><div class="v">{n_ma}</div></div>
    <div><div class="k">Paper logs</div><div class="v">{n_paper_logs}</div></div>
    <div><div class="k">Paper eligible</div><div class="v">{n_paper_ok}</div></div>
    <div><div class="k">STRICT</div><div class="v">{n_strict}</div></div>
  </div>

  <h2>Results by slice</h2>
  <div class="grid">
    {''.join(cards)}
  </div>

  <h2>Day-by-day (current arm path)</h2>
  <p class="sub">MA = live market-activity gate. PAPER = gate_approved paper log. STRICT = closest dashboard filter.</p>
  <div class="wrap">
    <table class="days">
      <thead>
        <tr>
          <th>Date</th><th>Ticker</th><th>MA</th><th>Paper</th><th>Strict</th>
          <th>Sim scenario</th><th>Sim net (current)</th>
        </tr>
      </thead>
      <tbody>
        {''.join(day_rows)}
      </tbody>
    </table>
  </div>

  <footer>
    Generated from compare_target_stop_30d_gated.json · backtest only · not a live rule change.
    yfinance pandas warnings during the run are harmless.
  </footer>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("data/compare_target_stop_30d_gated.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/compare_target_stop_30d_gated.html"),
    )
    # Optional: embed from stdin paste file
    parser.add_argument("--stdin-json", action="store_true")
    args = parser.parse_args()

    if args.stdin_json:
        payload = json.load(sys.stdin)
    else:
        if not args.json.is_file():
            print(f"ERROR: missing {args.json}", file=sys.stderr)
            return 2
        payload = json.loads(args.json.read_text())

    html_out = render(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_out)
    print(f"Wrote {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
