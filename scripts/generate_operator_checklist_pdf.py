#!/usr/bin/env python3
"""Generate one-page Phase 1B daily operator checklist PDF."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DAILY_OPERATOR_CHECKLIST.pdf"


class OperatorChecklistPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(110, 110, 110)
        self.cell(
            0,
            5,
            "AI Investment Agent | Phase 1B | v0.9 | E*TRADE manual | http://127.0.0.1:8080/operator-checklist.pdf",
            align="C",
        )


def _section(pdf: FPDF, w: float, title: str, lines: list[str], *, line_h: float = 3.5) -> None:
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4.5, title, ln=True)
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(25, 25, 25)
    for line in lines:
        pdf.multi_cell(w, line_h, line)
    pdf.ln(0.5)


def build_pdf(path: Path) -> Path:
    pdf = OperatorChecklistPDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    pdf.set_margins(11, 9, 11)
    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(15, 45, 95)
    pdf.cell(w, 7, "AI Investment Agent - Daily Operator Checklist (Phase 1B)", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(55, 55, 55)
    pdf.multi_cell(
        w,
        3.6,
        "You execute in E*TRADE. The dashboard screens, scores, alerts, and records. "
        "No auto-orders. Journal is source of truth for P&L and weekly counts.",
    )
    pdf.ln(0.5)

    pdf.set_fill_color(235, 242, 252)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 40, 80)
    pdf.multi_cell(
        w,
        3.8,
        "Decision stack:  (1) Market Activity day gate  ->  (2) Stock confirmation  ->  "
        "(3) Trading-day GO panel (time, targets, risk, stops)",
        fill=True,
    )
    pdf.ln(1)

    _section(
        pdf,
        w,
        "BEFORE THE OPEN",
        [
            "[ ] Setup tab: Daily ingest (or auto-refresh 6:30 AM PT)",
            "[ ] Screen tab: Run screener after ingest (14-day rank)",
        ],
    )

    _section(
        pdf,
        w,
        "MORNING - BEFORE 10:00 AM ET (7:00 AM PT)",
        [
            "[ ] Screen tab: Prepare today's trades (Step 2 - buy / sell / stop columns)",
            "[ ] Trade tab: Generate proposals (optional - up to 5 ranked setups)",
        ],
    )

    _section(
        pdf,
        w,
        "TRADE WINDOW - 10:00 AM to 2:30 PM ET",
        [
            "[ ] Trade tab: Refresh live before buy (updates MA, confirmation, top pick)",
            "[ ] Read status bar: Session verdict | Today $net / daily | Week n of 3 / weekly",
            "[ ] Check banners: RED = DO NOT TRADE | ORANGE = EXIT (sell at market) | PURPLE = Exceptional +1",
            "[ ] If GO: place limit buy in E*TRADE (deadline 11:30 AM ET - no chase if missed)",
            "[ ] Approve proposal (if used) -> execute -> Account tab: Log trade (link proposal on BUY)",
            "[ ] Refresh live before any second entry; max 2 open positions",
        ],
        line_h=3.4,
    )

    _section(
        pdf,
        w,
        "AFTER THE CLOSE",
        [
            "[ ] Review tab: Generate learning report",
            "[ ] Confirm flat or document overnight; journal matches E*TRADE",
        ],
    )

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4.5, "DAY GATE - MARKET ACTIVITY (new entries)", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(25, 25, 25)
    gates = [
        ("Exceptional (90+)", "Yes - ranked #1-#3 if each confirms"),
        ("Above average (75+)", "Yes - #1 primary"),
        ("Average & below (<75)", "NO TRADE - ranked list visible, no new entries"),
        ("Not bull (SPY 20d + weak session)", "NO TRADE regardless of score"),
    ]
    c0, c1 = w * 0.32, w * 0.68
    pdf.set_font("Helvetica", "B", 7.2)
    pdf.set_fill_color(225, 230, 240)
    pdf.cell(c0, 4.5, "Band", border=1, fill=True)
    pdf.cell(c1, 4.5, "New entries?", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 7.2)
    for band, rule in gates:
        pdf.cell(c0, 4.5, band, border=1)
        pdf.cell(c1, 4.5, rule, border=1, ln=True)
    pdf.ln(0.8)

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4.5, "WEEKLY PRODUCTION ($10K tier example)", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.multi_cell(
        w,
        3.4,
        "Daily target $150 | Weekly guidance 3 x $150 = $450 net (any day mix). "
        "One opportunity = closed win >= 67% of daily target OR stop-out. "
        "Weekly met = default stop. Exceptional override: max 1 extra/week when all signals GO.",
    )
    pdf.ln(0.5)

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4.5, "HARD RULES", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    rules = [
        "Confirmation never overrides a NO TRADE day.",
        "Stop-out logged today = no more entries (revenge trades blocked).",
        "Daily target hit = stop unless purple Exceptional override active.",
        "Every BUY has a stop (~0.75%). Target sized for net daily goal after $7+$7 fees.",
        "Start in Paper mode (Account tab) until rhythm is comfortable.",
    ]
    for rule in rules:
        pdf.multi_cell(w, 3.3, f"  -  {rule}")
    pdf.ln(0.5)

    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4.5, "DASHBOARD TABS", ln=True)
    tabs = [
        ("Trade", "Go/no-go, MA score, confirmations, top pick, proposals, alerts"),
        ("Screen", "Ranked screener, watchlist, Step 2 morning prep"),
        ("Review", "Learning report, close reports, CIO summary"),
        ("Account", "Journal (log trades), cash, goal %, paper/live mode"),
        ("Setup", "Ingest, watchlist load, auto-refresh install"),
    ]
    c0, c1 = w * 0.16, w * 0.84
    pdf.set_font("Helvetica", "B", 7.2)
    pdf.set_fill_color(225, 230, 240)
    pdf.cell(c0, 4.5, "Tab", border=1, fill=True)
    pdf.cell(c1, 4.5, "Use for", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 7.2)
    for tab, use in tabs:
        pdf.cell(c0, 4.5, tab, border=1)
        pdf.cell(c1, 4.5, use, border=1, ln=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def main() -> None:
    out = build_pdf(OUT)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
