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
    CEILING,
    OFFER,
    PERMITS,
    PRIOR_SALE,
    SELLER_TAX_BILL,
    SUPPORTED,
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
            "13994 Siena Loop   ·   Permits checked 23 Oct 2026, Pacific   ·   Original 2006 roof   ·   One HVAC permit, May 2024",
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
    supported = SUPPORTED
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
    pdf.cell(pdf.content_w, 5, "Pricing after the Manatee County permit check", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.boxes(
        [
            (money(OFFER), f"Opening offer.\nAbout {psf(OFFER / LIVING_SF)} per foot.", WARM),
            (money(supported), f"Supported value.\nAbout {psf(supported / LIVING_SF)} per foot.", BAND),
            (money(CEILING), f"Ceiling.\nAbout {psf(CEILING / LIVING_SF)} per foot.", GREEN),
        ]
    )
    pdf.body(
        "Manatee County permits confirm the tile roof is original, which matches the agent's statement that it is 20 years old. Permit CMP-05031188 was completed on 28 Feb 2006, "
        "and no reroof permit follows it. The only later mechanical permit is BLD2405-3790, one like-for-like air-conditioner "
        f"changeout issued 30 May 2024 for $9,524. That removes the old high case near {money(1_030_000)}. "
        "It does not confirm the agent's second system from 2017 or a pool heater from 2020. Those two dates are not in the public file, "
        "so they are not credits. Supported value stays on the 13978 contract rate for this floor plan, "
        f"about {money(round(twin, -3))}. Open at {money(OFFER)}. Do not go above {money(CEILING)} unless the insurance binder is affordable, "
        "the roof report does not require immediate replacement, and the second system's data plate is 2017 or newer. "
        f"The ask is {money(ASK - supported)} above the supported value. "
        f"County market value on the 2025 roll is {money(MARKET_VALUE)}. The owners bought the house on 21 May 2020 for {money(PRIOR_SALE)}."
    )

    pdf.h2("The house")
    pdf.fact_table(
        [
            ("List", f"{money(ASK)}  ·  MLS A4704244  ·  Coldwell Banker, Katina and Kenneth Shanahan"),
            ("Size", f"{LIVING_SF:,} living sq ft  ·  {TOTAL_SF:,} total building sq ft  ·  one story  ·  built 2006"),
            ("Rooms", "3 bedrooms, 3 baths, plus an office. The third bath serves the office and the pool."),
            ("Lot and view", "0.23 acres, lot 47. Golf course and lake view. Front faces east; lanai faces west."),
            ("County permits", "Original tile roof completed 28 Feb 2006. One HVAC changeout issued 30 May 2024. No 2017 HVAC permit. No 2020 heater permit."),
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
                comp["address"],
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
        [40, 28, 22, 16, 14, 68],
        ["LEFT", "LEFT", "RIGHT", "RIGHT", "RIGHT", "LEFT"],
    )
    pdf.body(
        "13978 is the cleanest comparison: same bedroom count, three baths, an office, and a golf-and-lake lot, "
        "plus a 4-ton 16 SEER air conditioner replaced in April 2026. It found a buyer at $899,000. "
        "13911 opened at $1,295,000 on 16 Jan 2026 and was cut to $995,000 by 20 Aug 2026, with more bedrooms and baths, and it was still for sale. "
        "13987 sold in the week of 3 Aug 2026 for $760,000 after a 2023 sale at $810,000."
    )
    pdf.body(
        "13828 closed at $799,000 on 1 Jun 2026 with a brand-new tile roof, a new pool heater, and a rescreened cage, "
        f"at {psf(price_per_sf(799_000, 2311))} per living foot. That is the top of the 2026 sold range. "
        "This house's roof, pool, and cage are the 2006 originals."
    )

    pdf.h2("What the remodel adds")
    pdf.body(
        "The May 2019 listing already advertised the pool, spa, outdoor kitchen, 18-inch tile, 48-inch cabinets, "
        "a granite island, and an office bath. None of that later finish work has a permit."
    )
    pdf.simple_table(
        ["Claimed in 2026", "Already true in 2019", "How to treat it"],
        [
            ["Quartz island", "Granite island", "Likely replaced. No permit."],
            ["Cabinets and primary shower", "Tall cabinets, tub, spa shower", "Finish work. No bath permit."],
            ["Pool, spa, cage", "Same features in 2019", "Original 2006 permits. Heater has none."],
            ["Roof", "Not described as new", "Original tile, completed 28 Feb 2006."],
            ["Two air conditioners", "Agent: 2024 and 2017", "Only the 2024 changeout is permitted."],
            ["Pool heater", "Agent: 2020", "No county permit. Require the data plate."],
        ],
        [52, 62, 74],
    )

    pdf.add_page()
    pdf.h2("What the county permits show")
    pdf.body(
        "Checked 23 Oct 2026 on the Manatee County public site. The historical permit files cover 2004 through 21 Feb 2018. "
        "The live permit layer, searched by parcel 588502359 and by 13994 SIENA, has one building permit, plus a pointer to the historical archive. "
        "\"None found\" means that work was not in those files. It does not by itself prove the equipment was never changed."
    )
    pdf.simple_table(
        ["Work", "Permit", "County result"],
        [[item["work"], item["permit"], item["pdf"]] for item in PERMITS],
        [48, 32, 108],
    )
    pdf.note(
        "BLD2405-3790 is Mechanical Express, project description \"Moriarty HVAC CHANGEOUT. LIKE FOR LIKE,\" "
        "no duct replacement, mechanical trade only. Record status is Closed. The Accela page still says there are no completed inspections."
    )

    pdf.h2("Carrying costs the ask does not show")
    pdf.body(
        "The sellers have homestead, so Save Our Homes is holding the assessed value at "
        f"{money(ASSESSED_VALUE)}. A buyer does not inherit that cap. The figures below use the 2025 millage of 14.160 "
        "and the same non-ad valorem charges. A homestead the next year assumes the standard exemptions and no portability. "
        "A buyer who ports a Florida homestead cap would pay less."
    )
    pdf.simple_table(
        ["Item", "Seller, 2025", "Buyer at the ask", "Buyer at $880,000"],
        [
            ["Price", "Already owned", money(ASK), money(supported)],
            ["Tax bill, year 1", money(SELLER_TAX_BILL), money(year1), money(non_homestead_tax(supported))],
            ["Tax bill, year 2 with homestead", money(SELLER_TAX_BILL), money(year2), money(homestead_tax(supported))],
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
        "The CDD is already inside that bill. Proposed FY2026/27 Siena CDD total is $3,782. "
        "Neighbor listings put Siena maintenance at $175 to $188 a month; confirm both associations on the estoppel. "
        "Club membership is optional and does not transfer. The 2026 Premier golf packet is $110,000 to join and $1,360 a month."
    )

    pdf.h2("Risk, in the order it can cost money")
    pdf.simple_table(
        ["Risk", "Level", "What is open"],
        [
            ["Price and resale", "High", "The ask is the outlier. 13911 has already been cut 23 percent and was still listed. 13987 sold in 2026 below its 2023 price."],
            ["Roof and insurance", "High", "Permit CMP-05031188 completed 28 Feb 2006 with the original tile roof. No reroof permit. Planning range to replace tile is $40,000 to $80,000. That is not a bid."],
            ["Second HVAC, water heater", "High", "Only BLD2405-3790, one 2024 changeout for $9,524. No 2017 permit and no water-heater permit. Read both data plates."],
            ["Tax reset", "High", f"About {money(year1 - SELLER_TAX_BILL)} more per year at the ask than the homestead bill."],
            ["Remodel, pool, and cage", "Medium", "No kitchen or bath permit. Pool completed 25 May 2006. Cage completed 7 Mar 2006. No 2020 heater permit."],
            ["HOA, flood, bedrooms", "Medium", "Town Hall fee is $135 a year; Siena maintenance is separate. Flood zone X. The office is not a fourth bedroom. The golf view did not get 13978 a premium."],
        ],
        [42, 22, 124],
    )

    pdf.h2("Pricing recommendation")
    pdf.body(
        f"Offer {money(OFFER)}. Supported value is {money(supported)}, about {psf(supported / LIVING_SF)} per living foot, "
        "in line with the 13978 contract once this house's living area is used. "
        "The permitted 2024 changeout is one system at a $9,524 job value. It offsets part of the original roof. It is not a premium. "
        "The 2017 air conditioner and the 2020 pool heater are not in the county file, so do not pay for them. "
        f"Do not exceed {money(CEILING)}. Go there only if the insurance binder is affordable, the roof certification does not call for immediate replacement, "
        "and the second system's data plate or invoice shows 2017 or newer. "
        f"The {money(ASK)} ask is {money(ASK - supported)} above the supported value."
    )
    pdf.body(
        "Still require a roof certification, a 4-point, a wind-mitigation report, a wood-destroying-organism inspection, "
        "a pool inspection, and both estoppels. Photograph both air-conditioner data plates and the pool-heater and water-heater plates."
    )
    pdf.h2("Sources")
    pdf.note(
        "MLS A4704244 and prior MLS A4436936, read 23 Oct 2026. Manatee County 2025 tax bill, parcel 588502359, "
        "payment posted 1 Dec 2025. Stellar MLS reprints for 13978 (A4705315), 13911 (A4678185), 13860 (TB8526072), "
        "13853 (A4666855), 13828 (A4687316), 13804 (A4691647), 13876, 13861 (A4668432), and 13844 (A4671692). "
        "Your Observer, 18 Aug 2026, for the 13987 sale. Lakewood Ranch CDD 5 FY2026/27 hearing notice for the proposed Siena assessment. "
        "Lakewood Ranch Golf & Country Club 2026 membership packet for dues. "
        "Permits: Manatee historical files 2004 through 21 Feb 2018, the live GIS PermitData layer, and Accela record BLD2405-3790, all read 23 Oct 2026. "
        "The agent's 2017 HVAC date and 2020 heater date remain the agent's statements. Repair ranges are planning numbers, not contractor bids."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(path)
    return path


def _short_note(comp: dict) -> str:
    notes = {
        "13994 Siena Loop": "Original 2006 roof. One HVAC permit, 2024.",
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
