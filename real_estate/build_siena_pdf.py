"""Printable desk brief for 13994 Siena Loop.

Numbers come from real_estate.siena_comps so the PDF and the workbook match.
The PDF embeds Inter, so it does not depend on fonts on the machine that opens it.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fpdf import FPDF
from fpdf.fonts import FontFace

from real_estate.siena_comps import (
    AD_VALOREM,
    ASK,
    ASSESSED_VALUE,
    CDD_DEBT,
    CDD_OM,
    FIRE_NON_AD,
    LIVING_SF,
    MARKET_VALUE,
    NON_AD_VALOREM,
    PRIOR_SALE,
    SELLER_TAX_BILL,
    TOTAL_SF,
    COMPS,
    homestead_tax,
    non_homestead_tax,
    price_per_sf,
    sold_median_ppsf,
    twin_implied_value,
)

OUT = ROOT / "real_estate" / "13994-Siena-Loop-valuation.pdf"
DESKTOP_NAME = "13994 Siena Loop - Lakewood Ranch valuation.pdf"
FONT_DIR = Path("/usr/share/fonts/truetype/macos")

NAVY = (31, 78, 121)
INK = (28, 32, 38)
MUTED = (78, 86, 96)
LINE = (214, 220, 226)
PAPER = (255, 255, 255)
BAND = (241, 245, 249)
WARM = (255, 244, 230)
ROSE = (252, 236, 232)
GREEN = (232, 243, 234)
AMBER = (166, 92, 20)
RED = (148, 48, 40)


def money(value: float) -> str:
    return f"${value:,.0f}"


def psf(value: float) -> str:
    return f"${value:,.0f}"


class Brief(FPDF):
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
        self.cell(
            0,
            4.5,
            "13994 Siena Loop   ·   Lakewood Ranch Country Club   ·   Desk comparison   ·   23 Oct 2026, Pacific",
            align="L",
        )
        self.set_xy(self.l_margin, 16)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_draw_color(*LINE)
        self.line(14, self.get_y(), self.w - 14, self.get_y())
        self.set_y(-10)
        self.set_font("Inter", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(0, 4, "Living area only. Desk comparison, not an appraisal. Parcel 588502359.", align="L")
        self.set_xy(self.w - 28, -10)
        self.cell(14, 4, str(self.page_no()), align="R")

    @property
    def content_w(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def h1(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "B", 20)
        self.set_text_color(*NAVY)
        self.multi_cell(self.content_w, 8, text)
        self.ln(1)

    def lede(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "", 10)
        self.set_text_color(*INK)
        self.multi_cell(self.content_w, 4.8, text, align="L")
        self.ln(2)

    def h2(self, text: str) -> None:
        if self.get_y() > self.h - 48:
            self.add_page()
        self.ln(1)
        self.set_x(self.l_margin)
        self.set_font("Inter", "B", 13)
        self.set_text_color(*NAVY)
        self.cell(self.content_w, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*NAVY)
        y = self.get_y()
        self.line(self.l_margin, y, self.l_margin + self.content_w, y)
        self.ln(2.5)

    def body(self, text: str, size: float = 9.5) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "", size)
        self.set_text_color(*INK)
        self.multi_cell(self.content_w, 4.5, text, align="L")
        self.ln(1.5)

    def note(self, text: str) -> None:
        self.set_x(self.l_margin)
        self.set_font("Inter", "", 8)
        self.set_text_color(*MUTED)
        self.multi_cell(self.content_w, 3.8, text, align="L")
        self.ln(1.5)

    def callout(self, title: str, text: str, fill: tuple[int, int, int], bar: tuple[int, int, int]) -> None:
        self.set_font("Inter", "", 9)
        # Measure height from wrapped text.
        lines = self.multi_cell(self.content_w - 10, 4.4, text, dry_run=True, output="LINES", align="L")
        height = 8 + 4.4 * len(lines) + 4
        if self.get_y() + height > self.h - 16:
            self.add_page()
        x, y = self.l_margin, self.get_y()
        self.set_fill_color(*fill)
        self.rect(x, y, self.content_w, height, "F")
        self.set_fill_color(*bar)
        self.rect(x, y, 2.2, height, "F")
        self.set_xy(x + 6, y + 2.5)
        self.set_font("Inter", "B", 10)
        self.set_text_color(*bar)
        self.cell(self.content_w - 10, 5, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(x + 6)
        self.set_font("Inter", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(self.content_w - 12, 4.4, text, align="L")
        self.set_y(y + height + 3)

    def boxes(self, items: list[tuple[str, str, tuple[int, int, int]]]) -> None:
        gap = 3
        n = len(items)
        width = (self.content_w - gap * (n - 1)) / n
        y = self.get_y()
        height = 20
        if y + height > self.h - 16:
            self.add_page()
            y = self.get_y()
        x = self.l_margin
        for value, label, fill in items:
            self.set_fill_color(*fill)
            self.rect(x, y, width, height, "F")
            self.set_xy(x + 3, y + 2.5)
            self.set_font("Inter", "B", 13)
            self.set_text_color(*NAVY)
            self.cell(width - 6, 6, value)
            self.set_xy(x + 3, y + 10)
            self.set_font("Inter", "", 7.5)
            self.set_text_color(*INK)
            self.multi_cell(width - 6, 3.4, label, align="L")
            x += width + gap
        self.set_xy(self.l_margin, y + height + 4)

    def fact_table(self, rows: list[tuple[str, str]]) -> None:
        label_w = 52
        value_w = self.content_w - label_w
        for i, (label, value) in enumerate(rows):
            self.set_font("Inter", "", 8.5)
            value_lines = self.multi_cell(value_w - 4, 4, value, dry_run=True, output="LINES", align="L")
            height = max(7, 4 * len(value_lines) + 2.4)
            if self.get_y() + height > self.h - 16:
                self.add_page()
            y = self.get_y()
            fill = BAND if i % 2 == 0 else PAPER
            self.set_fill_color(*fill)
            self.rect(self.l_margin, y, self.content_w, height, "F")
            self.set_xy(self.l_margin + 2, y + 1.2)
            self.set_font("InterM", "", 8.5)
            self.set_text_color(*NAVY)
            self.cell(label_w - 3, 4.2, label)
            self.set_xy(self.l_margin + label_w, y + 1.2)
            self.set_font("Inter", "", 8.5)
            self.set_text_color(*INK)
            self.multi_cell(value_w - 3, 4, value, align="L")
            self.set_y(y + height)

    def simple_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        widths: list[float],
        aligns: list[str] | None = None,
    ) -> None:
        self.set_font("Inter", "", 8)
        self.set_text_color(*INK)
        face = FontFace(family="Inter", emphasis="BOLD", size_pt=7.5, color=(255, 255, 255), fill_color=NAVY)
        with self.table(
            width=self.content_w,
            col_widths=tuple(widths),
            headings_style=face,
            line_height=3.6,
            text_align=tuple(aligns or ["LEFT"] * len(headers)),
            padding=1.2,
            borders_layout="HORIZONTAL_LINES",
            first_row_as_headings=True,
        ) as table:
            head = table.row()
            for header in headers:
                head.cell(header)
            for values in rows:
                row = table.row()
                for value in values:
                    row.cell(value)
        self.ln(2)


def build_pdf(path: Path = OUT) -> Path:
    ask_psf = price_per_sf(ASK, LIVING_SF)
    median_psf = sold_median_ppsf()
    twin = twin_implied_value()
    gap = ASK - twin
    mid = 940_000
    year1 = non_homestead_tax(ASK)
    year2 = homestead_tax(ASK)

    pdf = Brief()
    pdf.add_page()
    pdf.h1("This ask is above the street")
    pdf.lede(
        "The typed address, 13394 Siena Loop, is not a Manatee County parcel. "
        "The active listing is 13994 Siena Loop, MLS A4704244, in Siena at Lakewood Ranch Country Club."
    )
    pdf.callout(
        f"Ask {money(ASK)}  ·  {psf(ask_psf)} per living foot",
        f"Six 2026 sales on Siena Loop closed at a median of {psf(median_psf)} per living foot. "
        f"13978 Siena Loop, the same 3-bed, 3-bath, office, golf-and-lake plan, went under contract "
        f"at a {money(899_000)} ask, which is {psf(price_per_sf(899_000, 2673))} per foot. "
        f"Sized to this house, that rate is about {money(round(twin, -3))}. The ask is about {money(round(gap, -3))} above it. "
        "Listed 4 Sep 2026. On 23 Oct 2026 it was day 49, with no price cut.",
        ROSE,
        RED,
    )

    pdf.set_font("InterM", "", 9)
    pdf.set_text_color(*NAVY)
    pdf.set_x(pdf.l_margin)
    pdf.cell(pdf.content_w, 5, "Desk value, conditional on the roof and the air conditioner", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.boxes(
        [
            (money(860_000), "Original roof and AC.\nAbout $328 per foot.", WARM),
            (money(mid), "Systems still have life.\nAbout $358 per foot.", BAND),
            (money(1_030_000), "Roof and AC are recent.\nAbout $393 per foot.", GREEN),
        ]
    )
    pdf.body(
        f"The middle case pays a modest finish premium over 13978 and assumes the roof and air conditioner "
        f"still have useful life. County market value on the 2025 roll is {money(MARKET_VALUE)}. "
        f"The owners bought the house on 21 May 2020 for {money(PRIOR_SALE)}, after a 2019 listing that opened at $540,000."
    )

    pdf.h2("The house")
    pdf.fact_table(
        [
            ("List", f"{money(ASK)}  ·  MLS A4704244  ·  Coldwell Banker, Katina and Kenneth Shanahan"),
            ("Size", f"{LIVING_SF:,} living sq ft  ·  {TOTAL_SF:,} total building sq ft  ·  one story  ·  built 2006"),
            ("Rooms", "3 bedrooms, 3 baths, plus an office. The third bath serves the office and the pool."),
            ("Lot and view", "0.23 acres, lot 47. Golf course and lake view. Front faces east; lanai faces west."),
            ("Roof and pool", "Tile roof, year not stated. Heated pool and spa, screen cage, outdoor kitchen."),
            ("Flood", "Flood zone X on the listing detail. The lake is a view. MLS waterfront flag is No."),
            ("Parcel", "588502359. Country Club Village subphase R, Siena, and subphase S, Mizner Reserve."),
            ("Last sale", f"{money(PRIOR_SALE)} on 21 May 2020. Prior MLS A4436936."),
            ("2025 tax roll", f"Market {money(MARKET_VALUE)}. Assessed {money(ASSESSED_VALUE)}. Homestead."),
            ("2025 tax bill", f"{money(SELLER_TAX_BILL)}. Ad valorem ${AD_VALOREM:,.0f}. Non-ad valorem ${NON_AD_VALOREM:,.0f}."),
            ("Inside that bill", f"CDD operations ${CDD_OM:,.0f}, CDD debt ${CDD_DEBT:,.0f}, East Manatee fire ${FIRE_NON_AD:,.0f}."),
            ("MLS dues line", "$135 per year to Lakewood Ranch Town Hall. That is not the Siena maintenance fee."),
        ]
    )
    pdf.ln(2)
    pdf.note(
        f"Dividing the ask by the {TOTAL_SF:,} sq ft total building area prints about {psf(ASK / TOTAL_SF)} per foot. "
        "That denominator includes garage and lanai. Every comparison in this brief uses living area."
    )

    pdf.add_page()
    pdf.h2("Same-street sales and listings")
    pdf.body(
        "All prices per foot use public-record living area. Active prices are asks. "
        "The 13978 price is the ask it went under contract at; the contract price is not published and may be lower. "
        "The 13860 original ask is inferred from a reported 5.4 percent cut."
    )

    comp_rows = []
    for comp in COMPS:
        rate = price_per_sf(comp["price"], comp["living_sf"])
        status = comp["status"]
        if comp["role"] == "Subject":
            status = "Active, day 49"
        elif status.startswith("Under contract"):
            status = "In contract"
        comp_rows.append(
            [
                comp["address"].replace(" Siena Loop", ""),
                status.replace("Sold ", "Sold "),
                money(comp["price"]),
                f"{comp['living_sf']:,}",
                psf(rate),
                _short_note(comp),
            ]
        )
    pdf.simple_table(
        ["Address", "Status", "Price", "Living sf", "$/sf", "What matters"],
        comp_rows,
        [28, 32, 22, 18, 14, 74],
        ["LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT", "LEFT"],
    )
    pdf.body(
        "13978 is the cleanest comparison: same bedroom count, three baths, an office, and a golf-and-lake lot, "
        "plus a 4-ton 16 SEER air conditioner replaced in April 2026. It found a buyer at $899,000."
    )
    pdf.body(
        "13911 shows what an ambitious ask does on this loop. It opened at $1,295,000 on 16 Jan 2026 and was cut "
        "to $995,000 by 20 Aug 2026. It is larger, has four bedrooms and 3.5 baths, a 2024 air conditioner, and a 3-car garage, "
        "and it was still for sale. 13987 sold in the week of 3 Aug 2026 for $760,000 after a 2023 sale at $810,000."
    )
    pdf.body(
        "13828 closed at $799,000 on 1 Jun 2026 with a brand-new tile roof, a new pool heater, and a rescreened cage, "
        f"at {psf(price_per_sf(799_000, 2311))} per living foot. That is the top of the 2026 sold range, and the roof was the headline."
    )

    pdf.h2("What the remodel adds")
    pdf.body(
        "The current remarks describe a full remodel. The May 2019 remarks, when this house was listed and then sold "
        "for $445,000, already advertised the pool, spa, outdoor kitchen, 18-inch tile, 48-inch cabinets, a granite island, "
        "stainless appliances, a gas range, and an office with its own bath."
    )
    pdf.simple_table(
        ["Claimed in 2026", "Already true in 2019", "How to treat it"],
        [
            ["Quartz island", "Granite island", "Likely replaced. A real, limited premium."],
            ["New cabinetry and pantry", "48-inch cabinets, walk-in pantry", "Confirm they are new."],
            ["Frameless primary shower", "Tub, spa shower, two vanities", "Finish work in the same room."],
            ["Guest baths remodeled", "Three baths already", "Cosmetic unless permits show a rebuild."],
            ["Tile floors", "18-inch tile", "Existing."],
            ["Pool, spa, cage, outdoor kitchen", "Same features in the 2019 copy", "Existing. Ages are not disclosed."],
            ["Wine bar, electric fireplace", "Not in the 2019 remarks", "Cosmetic. The fireplace is electric."],
            ["Softener and closet system", "Two walk-in closets", "Useful. Small dollars."],
            ["Roof, AC, water heater", "No dates then either", "Open. Neighbors date 2023-2026 gear."],
        ],
        [58, 62, 68],
    )
    pdf.note(
        "Redfin shows a 2012 renovation year on its public-record pane. Treat that field as unverified until the Manatee permit file is pulled."
    )

    pdf.add_page()
    pdf.h2("Carrying costs the ask does not show")
    pdf.body(
        "The sellers have homestead, so Save Our Homes is holding the assessed value at "
        f"{money(ASSESSED_VALUE)}. A buyer does not inherit that cap. The figures below use the 2025 millage of 14.160 "
        "and the same non-ad valorem charges. A homestead the next year assumes the standard exemptions and no portability. "
        "A buyer who ports a Florida homestead cap would pay less."
    )
    pdf.simple_table(
        ["Item", "Seller, 2025", "Buyer at the ask", "Buyer at $940,000"],
        [
            ["Price", "Already owned", money(ASK), money(mid)],
            ["Tax bill, year 1", money(SELLER_TAX_BILL), money(year1), money(non_homestead_tax(mid))],
            ["Tax bill, year 2 with homestead", money(SELLER_TAX_BILL), money(year2), money(homestead_tax(mid))],
            ["Town Hall fee", "$135 / year", "$135 / year", "$135 / year"],
            ["Siena maintenance, planning", "$186 / month", "$186 / month", "$186 / month"],
            ["Insurance", "Unknown", "Quote before writing", "Quote before writing"],
            ["Club membership", "Optional", "Optional", "Optional"],
        ],
        [62, 40, 43, 43],
        ["LEFT", "RIGHT", "RIGHT", "RIGHT"],
    )
    pdf.body(
        f"At the ask, year-1 taxes are about {money(year1)}, roughly {money(year1 - SELLER_TAX_BILL)} more per year than the bill the seller is paying. "
        "The CDD is already inside the $13,013 bill. Debt service is only $331 a year, so the bond is small. "
        "Operations continue. The proposed FY2026/27 Siena CDD total is $3,782, against $3,497 billed for 2025."
    )
    pdf.body(
        "Neighbor listings put the Siena maintenance fee at $175 to $188 per month. 13828 disclosed $186 and 13804 disclosed $188. "
        "Confirm both associations on the estoppel, including what the maintenance covers and whether a special assessment is open."
    )
    pdf.body(
        "Club membership does not transfer with the deed. The 2026 Lakewood Ranch Golf & Country Club packet lists "
        "Premier golf at $110,000 to join and $1,360 a month, Sports at $15,000 and $430 a month, and Social at $6,000 and $185 a month. "
        "Heritage Golf Group has owned the club since early 2024. Price a membership separately if it matters."
    )

    pdf.h2("Risk, in the order it can cost money")
    pdf.simple_table(
        ["Risk", "Level", "What is open"],
        [
            ["Price and resale", "High", "The ask is the outlier. 13911 has already been cut 23 percent and was still listed. 13987 sold in 2026 below its 2023 price."],
            ["Roof and insurance", "High", "2006 tile, year not disclosed. Underlayment is the failure point. Planning range to replace tile on a house this size is $40,000 to $80,000. That is not a bid."],
            ["HVAC and water heater", "High", "The listing is silent. Neighbors advertise 2023-2026 replacements. Planning range: $8,000 to $16,000 for a 4-ton system, $1,500 to $3,000 for a heater."],
            ["Tax reset", "High", f"About {money(year1 - SELLER_TAX_BILL)} more per year at the ask than the homestead bill."],
            ["Remodel story", "Medium", "Pool, tile, kitchen footprint, and the office bath were already in the 2019 listing. Pull permits before paying a remodel premium."],
            ["HOA disclosure", "Medium", "The $135 annual line is the Town Hall fee. The village maintenance fee is the one on the neighbors' listings."],
            ["Pool and cage", "Medium", "Heated pool and spa are real. Surface, equipment, and the 2006 aluminum cage are undated."],
            ["Three bedrooms", "Medium", "The third bath is the office and pool bath. 13911 offers more bedrooms and baths at a lower ask."],
            ["Golf lot", "Medium", "The view is real, and 13978 shows what buyers paid for the same view. Balls, mowers, and course chemicals come with the lot."],
            ["Flood, CDD, 2006 screen", "Low", "Flood zone X. CDD debt is small. Nothing reviewed here ties this address to Chinese drywall. A 2006 build still belongs on a stucco, flashing, and drywall screen."],
        ],
        [42, 22, 124],
    )

    pdf.h2("Before an offer")
    pdf.body(
        "Require a roof certification that states the underlayment age, a 4-point inspection, a wind-mitigation report, "
        "a wood-destroying-organism inspection, a pool inspection, an insurance binder, both estoppels, and the Manatee permit history. "
        f"A price near {money(mid)} is the supported case when those reports show remaining life in the roof and the air conditioner. "
        f"An original 2006 roof pulls the case toward {money(860_000)}. "
        f"The {money(ASK)} ask requires a buyer who sets aside the six 2026 sales and the under-contract house with the same view."
    )
    pdf.h2("Sources")
    pdf.note(
        "MLS A4704244 and prior MLS A4436936, read 23 Oct 2026. Manatee County 2025 tax bill, parcel 588502359, "
        "payment posted 1 Dec 2025. Stellar MLS reprints for 13978 (A4705315), 13911 (A4678185), 13860 (TB8526072), "
        "13853 (A4666855), 13828 (A4687316), 13804 (A4691647), 13876, 13861 (A4668432), and 13844 (A4671692). "
        "Your Observer, 18 Aug 2026, for the 13987 sale. Lakewood Ranch CDD 5 FY2026/27 hearing notice for the proposed Siena assessment. "
        "Lakewood Ranch Golf & Country Club 2026 membership packet for dues. Repair ranges are planning numbers, not contractor bids."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(path)
    return path


def _short_note(comp: dict) -> str:
    notes = {
        "13994 Siena Loop": "Subject. Golf and lake. Roof and AC undated.",
        "13978 Siena Loop": "Same plan and view. AC replaced Apr 2026.",
        "13853 Siena Loop": "Recent HVAC, heater, rescreen. Pond.",
        "13860 Siena Loop": "Larger. AC 2024, water heater 2025.",
        "13911 Siena Loop": "Cut from $1,295,000. More house. AC 2024.",
        "13828 Siena Loop": "New roof, new pool heater, rescreened.",
        "13804 Siena Loop": "Renovated. 0.35-acre pond lot.",
        "13987 Siena Loop": "Sold below its 2023 price of $810,000.",
        "13876 Siena Loop": "Closest sold size. Listed at $849,000.",
        "13861 Siena Loop": "HVAC 2023. Pool rebuilt. Listed $749,000.",
        "13844 Siena Loop": "Smaller 2-bedroom plan with a pool.",
    }
    return notes[comp["address"]]


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
