"""Family funding plan for a $1,125,000 purchase of 13994 Siena Loop.

Closing is 3 Dec 2026. The two paths are a loan that stays at 7.3 percent,
and a refinance at the end of 2027 that also applies $100,000 to principal.
Figures match the funding tables discussed 25 Oct 2026, Pacific.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fpdf import FPDF

OUT = ROOT / "real_estate" / "13994-Siena-Loop-family-plan.pdf"
DESKTOP_NAME = "13994 Siena Loop - family funding plan.pdf"
FONT_DIR = Path("/usr/share/fonts/truetype/macos")

NAVY = (31, 78, 121)
INK = (28, 32, 38)
MUTED = (78, 86, 96)
LINE = (214, 220, 226)
BAND = (241, 245, 249)
WARM = (255, 244, 230)
GREEN = (232, 243, 234)
WHITE = (255, 255, 255)

PRICE = 1_125_000
DOWN = 225_000
LOAN = 900_000
CALPERS = 5_100
SOCIAL = 1_100
TOWN = 11
SIENA = 186
INSURANCE = 1_000
BILLS = 500
FEDERAL = 0.22
SCHOOL_MILLS = 6.304
OTHER_MILLS = 7.856
NON_AD = 3_768.59


def payment(principal: float, annual: float, months: int = 360) -> float:
    rate = annual / 12
    return principal * rate * (1 + rate) ** months / ((1 + rate) ** months - 1)


def balance_after(principal: float, annual: float, payments_made: int, months: int = 360) -> float:
    rate = annual / 12
    paid = payment(principal, annual, months)
    return principal * (1 + rate) ** payments_made - paid * ((1 + rate) ** payments_made - 1) / rate


def annual_tax(other_exemption: int) -> float:
    school = (PRICE - 25_000) * SCHOOL_MILLS / 1000
    other = (PRICE - other_exemption) * OTHER_MILLS / 1000
    return school + other + NON_AD


def dollars(value: float) -> int:
    return int(round(value))


PI_73 = dollars(payment(LOAN, 0.073))
TAX_2027 = dollars(annual_tax(150_000) / 12)
TAX_2028 = dollars(annual_tax(250_000) / 12)
REFINANCE_BALANCE = dollars(balance_after(LOAN, 0.073, 12) - 100_000)
PI_65 = dollars(payment(REFINANCE_BALANCE, 0.065))

FIXED = TOWN + SIENA + INSURANCE + BILLS


def month_total(principal_and_interest: int, tax: int) -> int:
    return principal_and_interest + tax + FIXED


TOTAL_2027 = month_total(PI_73, TAX_2027)
TOTAL_STAY = month_total(PI_73, TAX_2028)
TOTAL_REFI = month_total(PI_65, TAX_2028)
GAP_2027 = TOTAL_2027 - CALPERS
GAP_STAY = TOTAL_STAY - CALPERS
GAP_STAY_SS = GAP_STAY - SOCIAL
GAP_REFI = TOTAL_REFI - CALPERS
GAP_REFI_SS = GAP_REFI - SOCIAL


def year_need(full_months: int, full_gap: int, reduced_months: int = 0, reduced_gap: int = 0) -> int:
    return full_months * full_gap + reduced_months * reduced_gap


CASH_2027 = year_need(12, GAP_2027)
STAY_2028 = year_need(3, GAP_STAY, 9, GAP_STAY_SS)
STAY_LATER = year_need(12, GAP_STAY_SS)
REFI_2028 = year_need(3, GAP_REFI, 9, GAP_REFI_SS)
REFI_LATER = year_need(12, GAP_REFI_SS)


def gross_withdrawal(spendable: int) -> int:
    if spendable == 0:
        return 0
    return dollars(spendable / (1 - FEDERAL))


def money(value: float) -> str:
    return f"${value:,.0f}"


class Plan(FPDF):
    def __init__(self) -> None:
        super().__init__(format="Letter", unit="mm")
        self.add_font("Inter", "", str(FONT_DIR / "Inter-Regular.ttf"))
        self.add_font("Inter", "B", str(FONT_DIR / "Inter-Bold.ttf"))
        self.add_font("InterM", "", str(FONT_DIR / "Inter-Medium.ttf"))
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(14, 16, 14)

    def header(self) -> None:
        self.set_fill_color(*NAVY)
        self.rect(0, 0, self.w, 11, "F")
        self.set_xy(14, 3.2)
        self.set_font("Inter", "", 8)
        self.set_text_color(255, 255, 255)
        self.cell(0, 4.5, "13994 Siena Loop   ·   Family funding plan   ·   25 Oct 2026, Pacific", align="L")
        self.set_xy(self.l_margin, 15)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_draw_color(*LINE)
        self.line(14, self.get_y(), self.w - 14, self.get_y())
        self.set_y(-10)
        self.set_font("Inter", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 4, "Funding plan for a stated purchase price. Not an appraisal or a tax return.", align="L")
        self.set_xy(self.w - 28, -10)
        self.cell(14, 4, str(self.page_no()), align="R")

    @property
    def content_w(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def heading(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "B", 16)
        self.set_text_color(*NAVY)
        self.multi_cell(self.content_w, 7, text)
        self.ln(1)

    def subhead(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "B", 12)
        self.set_text_color(*NAVY)
        self.multi_cell(self.content_w, 6, text)
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "", 9.5)
        self.set_text_color(*INK)
        self.multi_cell(self.content_w, 4.6, text)
        self.ln(1.6)

    def note(self, text: str, fill: tuple[int, int, int] = BAND) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "", 9)
        self.set_fill_color(*fill)
        self.set_text_color(*INK)
        y = self.get_y()
        self.multi_cell(self.content_w, 4.5, text, fill=True)
        self.rect(self.l_margin, y, self.content_w, self.get_y() - y)
        self.ln(2.2)

    def bullets(self, lines: list[str]) -> None:
        for line in lines:
            self.set_x(self.l_margin)
            self.set_font("Inter", "", 9.5)
            self.set_text_color(*INK)
            self.multi_cell(self.content_w, 4.6, f"•  {line}")
            self.ln(0.6)
        self.ln(1.4)

    def ensure(self, height: float) -> None:
        if self.get_y() + height > self.h - 16:
            self.add_page()

    def year_table(self, rows: list[tuple[str, list[str], str]], fill_header: tuple[int, int, int] = NAVY) -> None:
        label_w = 68
        col_w = (self.content_w - label_w) / 4
        headers = ["", "2027", "2028", "2029", "2030"]
        widths = [label_w, col_w, col_w, col_w, col_w]
        self.set_font("Inter", "B", 8)
        self.set_fill_color(*fill_header)
        self.set_text_color(*WHITE)
        self.set_x(self.l_margin)
        for index, header in enumerate(headers):
            self.cell(widths[index], 6.2, header, border=0, align="L" if index == 0 else "R", fill=True)
        self.ln()
        for label, values, kind in rows:
            if kind == "total":
                self.set_font("Inter", "B", 8)
                self.set_fill_color(226, 232, 240)
            elif kind == "gap":
                self.set_font("Inter", "B", 8)
                self.set_fill_color(255, 248, 230)
            else:
                self.set_font("Inter", "", 8)
                self.set_fill_color(*WHITE)
            self.set_text_color(*INK)
            self.set_x(self.l_margin)
            self.cell(widths[0], 5.8, label, border="B", fill=True)
            for value in values:
                self.cell(col_w, 5.8, value, border="B", align="R", fill=True)
            self.ln()
        self.ln(2)


def build_pdf(path: Path | None = None) -> Path:
    pdf = Plan()
    pdf.add_page()
    pdf.heading("How the Siena Loop purchase would be paid")
    pdf.body(
        "This is the funding plan for buying 13994 Siena Loop, Lakewood Ranch, Florida, "
        "for $1,125,000. Closing is December 3, 2026. The down payment is 20 percent, "
        "which is $225,000, so the starting loan is $900,000 at 7.3 percent for 30 years. "
        "The seller pays the 2026 property tax. The first tax bill in this plan is the one mailed in November 2027."
    )
    pdf.body(
        "Two versions of 2028 through 2030 are shown. In the first, the rate stays 7.3 percent and the extra "
        "$100,000 is not put on the loan. In the second, the rate is 6.5 percent or lower at the end of 2027, "
        "the loan is refinanced, and $100,000 from the investment account is paid onto the principal. "
        "That $100,000 is not a 401(k) withdrawal."
    )
    pdf.note(
        "A separate desk comparison of 2026 sales on this street supported about $880,000, "
        "with $910,000 as the top of that range. This funding plan uses $1,125,000, which is "
        "$429 per living square foot on 2,623 square feet. The payment math below does not change that comparison. "
        "The house was listed at $1,195,000. The owners had already turned down two offers under $1,000,000."
    )

    pdf.subhead("Where each dollar comes from")
    pdf.bullets(
        [
            "CalPERS pays $5,100 every month, in every year of this plan.",
            "A cash account pays the 2027 gap, about $4,297 a month, or $51,564 for the year.",
            "Social Security is estimated at $1,100 a month in the bank, starting April 2028. January, February, and March of 2028 are still the full gap.",
            "The 401(k) pays whatever CalPERS and Social Security do not cover, from 2028 through 2030. The withdrawal is taxed as ordinary income. The tables use a 22 percent federal rate. Florida does not add a state income tax.",
        ]
    )

    pdf.subhead("What one month includes")
    pdf.body(
        "Principal and interest is the loan payment only. Property tax includes the homestead exemption described below "
        "and the community development district charge, called the CDD. The CDD is about $3,497 of the annual tax bill "
        "and is not based on the price of the house. Its small debt piece, about $331 a year, ends after the May 2031 bond payment. "
        "The operations piece, about $3,166 and subject to the yearly budget, continues. Town Hall is $135 a year. "
        "Siena maintenance is $186 a month from neighboring listings and still needs the estoppel for this house. "
        "Insurance is a $1,000 a month placeholder until a binder quote. Household bills are a $500 estimate."
    )

    pdf.subhead("The homestead, and why 2027 is the first bill")
    pdf.body(
        "Florida sets the owner and the exemption on January 1. Closing on December 3, 2026 means the house is owned on January 1, 2027. "
        "The buyer is already a Florida resident. If Siena is the permanent home on January 1, 2027, and the homestead application is filed by March 1, 2027, "
        "the November 2027 tax bill carries the exemption. Only one Florida house can have homestead. Claiming it on Siena means it is not also claimed on another house."
    )
    pdf.body(
        "Amendment 3 on the November 2026 ballot, if 60 percent of voters approve it, sets the non-school exemption at $150,000 for 2027 and $250,000 for 2028 and after. "
        "School taxes keep a $25,000 exemption. The tables assume the amendment passes. If it fails, the ordinary homestead is smaller and the monthly tax is higher than the figures below. "
        "The CDD is a special assessment, so the amendment does not remove it."
    )

    pdf.add_page()
    pdf.heading("1. The rate stays at 7.3 percent")
    pdf.body(
        "No refinance. The extra $100,000 stays in the investment account and is not paid onto the loan. "
        "The loan remains $900,000 at 7.3 percent. In 2028 the homestead exemption rises from $150,000 to $250,000, which lowers the tax by $65 a month. That is the only change in the house payment."
    )
    pdf.year_table(
        [
            ("Loan the payment uses", [money(LOAN)] * 4, "plain"),
            ("Interest rate", ["7.3%"] * 4, "plain"),
            ("Homestead, non-school", ["$150,000", "$250,000", "$250,000", "$250,000"], "plain"),
            ("Principal and interest", [money(PI_73)] * 4, "plain"),
            ("Property tax", [money(TAX_2027), money(TAX_2028), money(TAX_2028), money(TAX_2028)], "plain"),
            ("Town Hall", [money(TOWN)] * 4, "plain"),
            ("Siena maintenance", [money(SIENA)] * 4, "plain"),
            ("Insurance", [money(INSURANCE)] * 4, "plain"),
            ("Monthly bills", [money(BILLS)] * 4, "plain"),
            ("Total monthly", [money(TOTAL_2027), money(TOTAL_STAY), money(TOTAL_STAY), money(TOTAL_STAY)], "total"),
            ("CalPERS", [money(CALPERS)] * 4, "plain"),
            ("Social Security", ["$0", "$1,100 in April", "$1,100", "$1,100"], "plain"),
            ("Left to cover", [money(GAP_2027), f"{money(GAP_STAY)} / {money(GAP_STAY_SS)}", money(GAP_STAY_SS), money(GAP_STAY_SS)], "gap"),
            ("Paid from", ["Cash account", "401(k)", "401(k)", "401(k)"], "plain"),
            ("Spendable for the year", [money(CASH_2027), money(STAY_2028), money(STAY_LATER), money(STAY_LATER)], "plain"),
            ("401(k) withdrawn, 22%", [money(0), money(gross_withdrawal(STAY_2028)), money(gross_withdrawal(STAY_LATER)), money(gross_withdrawal(STAY_LATER))], "plain"),
        ]
    )
    stay_spend = STAY_2028 + STAY_LATER * 2
    stay_gross = gross_withdrawal(STAY_2028) + gross_withdrawal(STAY_LATER) * 2
    pdf.note(
        f"Through 2030 the cash account provides {money(CASH_2027)} and the 401(k) provides {money(stay_spend)} of spending money. "
        f"At 22 percent federal tax, that spending takes {money(stay_gross)} out of the 401(k). "
        f"From 2031 on, about {money(GAP_STAY_SS)} a month is still left after CalPERS and Social Security.",
        WARM,
    )
    pdf.body(
        "In the 2028 left-to-cover cell, the first amount is January through March, before Social Security. "
        f"Those three months are {money(GAP_STAY)} each. The second amount is April through December, {money(GAP_STAY_SS)} each."
    )

    pdf.add_page()
    pdf.heading("2. Refinance at the end of 2027")
    pdf.body(
        "This path happens only if a 30-year rate of 6.5 percent, or lower, is available at the end of 2027. "
        "After a year of payments the loan balance is about $891,000. Paying $100,000 from the investment account onto the principal leaves about "
        f"{money(REFINANCE_BALANCE)} to refinance at 6.5 percent. The new principal-and-interest payment is {money(PI_65)}. "
        "Refinance closing costs are not subtracted from the $100,000 in this table. If they are paid from that $100,000, less money reaches the principal and the new payment is a little higher."
    )
    pdf.year_table(
        [
            ("Loan the payment uses", [money(LOAN), money(REFINANCE_BALANCE), money(REFINANCE_BALANCE), money(REFINANCE_BALANCE)], "plain"),
            ("Interest rate", ["7.3%", "6.5%", "6.5%", "6.5%"], "plain"),
            ("Homestead, non-school", ["$150,000", "$250,000", "$250,000", "$250,000"], "plain"),
            ("Principal and interest", [money(PI_73), money(PI_65), money(PI_65), money(PI_65)], "plain"),
            ("Property tax", [money(TAX_2027), money(TAX_2028), money(TAX_2028), money(TAX_2028)], "plain"),
            ("Town Hall", [money(TOWN)] * 4, "plain"),
            ("Siena maintenance", [money(SIENA)] * 4, "plain"),
            ("Insurance", [money(INSURANCE)] * 4, "plain"),
            ("Monthly bills", [money(BILLS)] * 4, "plain"),
            ("Total monthly", [money(TOTAL_2027), money(TOTAL_REFI), money(TOTAL_REFI), money(TOTAL_REFI)], "total"),
            ("CalPERS", [money(CALPERS)] * 4, "plain"),
            ("Social Security", ["$0", "$1,100 in April", "$1,100", "$1,100"], "plain"),
            ("Left to cover", [money(GAP_2027), f"{money(GAP_REFI)} / {money(GAP_REFI_SS)}", money(GAP_REFI_SS), money(GAP_REFI_SS)], "gap"),
            ("Paid from", ["Cash account", "401(k)", "401(k)", "401(k)"], "plain"),
            ("Spendable for the year", [money(CASH_2027), money(REFI_2028), money(REFI_LATER), money(REFI_LATER)], "plain"),
            ("401(k) withdrawn, 22%", [money(0), money(gross_withdrawal(REFI_2028)), money(gross_withdrawal(REFI_LATER)), money(gross_withdrawal(REFI_LATER))], "plain"),
        ],
        fill_header=(36, 92, 74),
    )
    refi_spend = REFI_2028 + REFI_LATER * 2
    refi_gross = gross_withdrawal(REFI_2028) + gross_withdrawal(REFI_LATER) * 2
    pdf.note(
        f"2027 is the same {money(CASH_2027)} from the cash account. From 2028 through 2030 the 401(k) provides {money(refi_spend)} of spending money, "
        f"which takes {money(refi_gross)} out of the account at 22 percent. "
        f"That is {money(stay_spend - refi_spend)} less spending, and {money(stay_gross - refi_gross)} less withdrawn, than the path with no refinance. "
        f"From 2031 on, about {money(GAP_REFI_SS)} a month is still left after CalPERS and Social Security.",
        GREEN,
    )
    pdf.body(
        f"The 2028 left-to-cover cell is the same split: {money(GAP_REFI)} for January through March, then {money(GAP_REFI_SS)} from April on. "
        "If the rate is still above 6.5 percent, this second table does not happen, and the first table is the one to use."
    )

    pdf.subhead("What the family can hold onto")
    pdf.bullets(
        [
            f"Both paths need the cash account to cover {money(CASH_2027)} in 2027. Social Security does not start until April 2028.",
            "The $250,000 homestead exemption is already inside the 2028, 2029, and 2030 tax lines of both tables. It is $1,465 a month, or $17,577 for the year.",
            f"The 401(k) amount is the sum used up by the end of 2030. It is not a balance that remains. A joint return may tax part of a withdrawal at 12 percent instead of 22 percent, which would make the withdrawn totals smaller.",
            "The $1,100 Social Security figure is the amount expected in the bank. If that estimate was made before the 2025 repeal of the windfall elimination provision, the current benefit may be higher. If April 2028 is before full retirement age, the reduction lasts for life.",
            "The original tile roof was completed in February 2006. A planning range to replace it is $40,000 to $80,000, and that cost is not in the monthly tables. One air conditioner has a 2024 permit. The second system and the pool heater were not found in the county permit file.",
            "Siena maintenance of $186 a month is from neighboring listings, not this house's estoppel. The Town Hall fee of $135 a year is separate from it.",
        ]
    )
    pdf.note(
        "Read the first table if the mortgage rate is still above 6.5 percent at the end of 2027. "
        "Read the second table if the loan is refinanced at 6.5 percent or lower and $100,000 is paid onto the principal. "
        "Either way, the monthly gap continues in 2031."
    )

    destination = path or OUT
    destination.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(destination)
    return destination


def copy_to_desktop(pdf_path: Path, desktop: Path | None = None) -> Path:
    folder = desktop or Path.home() / "Desktop"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / DESKTOP_NAME
    dest.write_bytes(pdf_path.read_bytes())
    return dest


def main() -> None:
    pdf_path = build_pdf()
    desktop = copy_to_desktop(pdf_path)
    print(pdf_path)
    print(desktop)


if __name__ == "__main__":
    main()
