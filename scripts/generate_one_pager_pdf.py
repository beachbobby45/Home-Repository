#!/usr/bin/env python3
"""Generate printable PDF for docs/DASHBOARD_ONE_PAGER.md content."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DASHBOARD_ONE_PAGER.pdf"


class OnePagerPDF(FPDF):
    def header(self) -> None:
        pass

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "AI Investment Agent v3 | E*TRADE manual | Option A (no Claude)", align="C")


def build_pdf(path: Path) -> Path:
    pdf = OnePagerPDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_margins(14, 12, 14)

    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(w, 10, "AI Investment Agent", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(w, 5, "Daily One-Pager  |  You trade in E*TRADE. This board screens, alerts, and records. No auto-orders.")
    pdf.ln(2)

    pdf.set_fill_color(240, 245, 252)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w, 7, "Strategy: +1.13% target  |  -0.50% stop  |  ~3% swing  |  $7 buy + $7 sell  |  $10K to $5M goal", ln=True, fill=True)
    pdf.ln(3)

    sections = [
        (
            "Before you start (once per session)",
            [
                "[ ] Dashboard open  |  APP_API_KEY pasted -> Save",
                "[ ] Regime banner GREEN (if red = SPY+DIA+QQQ all down -> NO new longs)",
            ],
        ),
        (
            "Morning (pre-market / open)",
            [
                "[ ] Refresh data: run_ingest.py OR Pull history + Sync from screener",
                "[ ] Read Market Brief (VIX + regime)",
                "[ ] Review Trade Queue - advance only names you agree with",
                "    watching -> approved -> armed -> alert -> in_trade -> eod -> closed",
                "[ ] Note Target +1.13%  |  Stop -0.50%  |  Size on each row",
            ],
        ),
        (
            "During market hours",
            [
                "[ ] Run monitor every 15-30 min (or on alert)",
                "[ ] On TARGET_HIT / STOP_HIT / EOD_FLATTEN:",
                "    1. Execute in E*TRADE",
                "    2. Log fill in Trade Journal (BUY or SELL)",
                "    3. Acknowledge alert on board",
                "[ ] Same-day flat default - close before close unless overnight approved",
            ],
        ),
        (
            "End of day",
            [
                "[ ] Final Run monitor",
                "[ ] All open positions closed in E*TRADE (or overnight exception documented)",
                "[ ] Every fill logged in Trade Journal (buy AND sell)",
                "[ ] Generate report (Learning)  |  skim CIO Summary",
                "[ ] Glance Historical Analysis - prior-day screener vs actual",
            ],
        ),
        (
            "End of month (if month P&L > 0)",
            [
                "[ ] Check Month-end Sweep Preview (10% mgmt + tax %)",
                "[ ] Adjust tax rate if needed -> Save rate",
                "[ ] Apply month-end sweep",
            ],
        ),
    ]

    for title, lines in sections:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(20, 40, 80)
        pdf.cell(w, 6, title, ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        for line in lines:
            pdf.multi_cell(w, 4.2, line)
        pdf.ln(1.5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(w, 6, "Quick reference", ln=True)
    pdf.ln(1)

    table = [
        ("Section", "Why"),
        ("Regime banner", "Gate for new longs"),
        ("Goal / Cash / Month P&L", "Account health"),
        ("Trade Queue", "What to watch / trade"),
        ("Intraday Alerts", "Target, stop, EOD"),
        ("Trade Journal", "Source of truth - log every fill"),
        ("Learning + CIO", "Daily feedback + actions"),
    ]
    col1 = w * 0.42
    col2 = w * 0.58
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(230, 235, 245)
    pdf.cell(col1, 5.5, table[0][0], border=1, fill=True)
    pdf.cell(col2, 5.5, table[0][1], border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for row in table[1:]:
        pdf.cell(col1, 5.5, row[0], border=1)
        pdf.cell(col2, 5.5, row[1], border=1, ln=True)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "Needs API key:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(
        w,
        4,
        "Sync queue  |  Run monitor  |  Pull history  |  Generate report  |  Log trade  |  Apply sweep",
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "CLI:", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(w, 4, "run_ingest.py  |  run_monitor.py  |  run_dashboard.py  |  run_learning.py")

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def main() -> None:
    out = build_pdf(OUT)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
