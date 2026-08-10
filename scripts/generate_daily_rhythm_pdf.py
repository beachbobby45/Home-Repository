#!/usr/bin/env python3
"""Generate one-page printable Daily Rhythm PDF for the dashboard Screen tab."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DAILY_RHYTHM_ONE_PAGE.pdf"


class DailyRhythmPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-11)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(110, 110, 110)
        self.cell(
            0,
            6,
            "AI Investment Agent | Growth Plan | E*TRADE manual | http://127.0.0.1:8080",
            align="C",
        )


def _section(pdf: FPDF, w: float, title: str, lines: list[str]) -> None:
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 5, title, ln=True)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(25, 25, 25)
    for line in lines:
        pdf.multi_cell(w, 3.8, line)
    pdf.ln(1)


def build_pdf(path: Path) -> Path:
    pdf = DailyRhythmPDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    pdf.set_margins(12, 10, 12)
    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15, 45, 95)
    pdf.cell(w, 8, "AI Investment Agent - Daily Rhythm", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(55, 55, 55)
    pdf.multi_cell(
        w,
        4,
        "One-page reference for Screen tab pills + Trade tab. Times are Eastern (ET). "
        "Pacific = ET minus 3 hours.",
    )
    pdf.ln(1)

    pdf.set_fill_color(235, 242, 252)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(20, 40, 80)
    pdf.multi_cell(
        w,
        4,
        "Morning chain:  Daily ingest  ->  Run screener  ->  Trade tab -> Refresh live",
        fill=True,
    )
    pdf.ln(2)

    _section(
        pdf,
        w,
        "ONE-TIME SETUP (do once, or when changing universe)",
        [
            "[ ] Screen -> S&P 500  (adds ~500 tickers; you already have ~537)",
            "[ ] Full ingest  OR  Terminal:  ./scripts/run_ingest_mac.sh  (15-25 min first time)",
            "[ ] Run screener",
            "    Goal: 'Missing metrics' near 0 on Screen tab stats line",
        ],
    )

    _section(
        pdf,
        w,
        "EVERY TRADING MORNING (before 10:00 AM ET / 7:00 AM PT)",
        [
            "[ ] Daily ingest  (updates overnight data; ~5-15 min)",
            "[ ] Run screener  (rebuilds 14-day rank + Step 3 list; ~1 min)",
            "[ ] Trade tab -> Refresh live  (live prices for Pick #1; ~15 sec)",
            "[ ] Read Pick #1 / Pick #2 and Planned purchase check before any E*TRADE buy",
            "    NO TRADES today is OK if nothing passes Step 3 + $150 tradability",
        ],
    )

    _section(
        pdf,
        w,
        "DURING THE MARKET (10:00 AM - 2:30 PM ET entry window)",
        [
            "[ ] Trade tab -> Refresh live  before you buy and every 30-60 min if watching",
            "[ ] Run monitor  ONLY if you have an open position (Screen tab)",
            "[ ] Do NOT run Full ingest during session (slow, locks database)",
            "[ ] Refresh ranked  = reload table only (no new market data)",
            "[ ] Execute in E*TRADE -> log fill in Account -> Trade journal",
        ],
    )

    _section(
        pdf,
        w,
        "AFTER THE CLOSE (optional, ~4:00-6:00 PM ET)",
        [
            "[ ] Daily ingest  ->  Run screener  (prepare tomorrow's rank)",
            "[ ] Review tab -> Daily close / Learning report",
            "[ ] Confirm all positions flat; journal matches E*TRADE",
        ],
    )

    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 5, "WHAT EACH SCREEN TAB PILL DOES", ln=True)
    pdf.ln(0.5)

    pills = [
        ("SP100 / S&P 500 / DC watch", "Add tickers to pool", "Once (setup)"),
        ("Full ingest", "Download ALL history + metrics", "Once, then weekly"),
        ("Daily ingest", "Update stale quotes + bars", "Every trading morning"),
        ("Run screener", "14-day rank + Step 3 pass list", "After every ingest"),
        ("Refresh ranked", "Reload table from database", "Anytime (display only)"),
    ]
    c0, c1, c2 = w * 0.28, w * 0.48, w * 0.24
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_fill_color(225, 230, 240)
    pdf.cell(c0, 5, "Button", border=1, fill=True)
    pdf.cell(c1, 5, "Purpose", border=1, fill=True)
    pdf.cell(c2, 5, "How often", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    for row in pills:
        pdf.cell(c0, 5, row[0], border=1)
        pdf.cell(c1, 5, row[1], border=1)
        pdf.cell(c2, 5, row[2], border=1, ln=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 100)
    pdf.cell(w, 4, "Timestamps:", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(
        w,
        3.6,
        "Under each pill on Screen tab: Last: [date/time PT] = when that action last finished. "
        "Terminal ingest counts after git pull. est. = estimated from older data.",
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(w, 4, "Terminal shortcuts (Mac):", ln=True)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.multi_cell(
        w,
        3.6,
        "Open Dashboard.command  |  ./scripts/run_ingest_mac.sh  |  "
        "./scripts/run_ingest_mac.sh --incremental  (daily)",
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(path))
    return path


def main() -> None:
    out = build_pdf(OUT)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
