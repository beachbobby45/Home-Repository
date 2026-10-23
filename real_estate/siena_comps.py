"""Desk comparison for 13994 Siena Loop, Lakewood Ranch.

The typed address 13394 Siena Loop does not match a Manatee County parcel.
The active listing on that street is 13994 Siena Loop, MLS A4704244.

Figures are public-record and listing facts gathered 23 Oct 2026. Dollar
opinions are a desk comparison, not an appraisal. Living area is the only
square footage used for price per foot. Several portals divide price by
total under-roof area and print a much lower number.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

SUBJECT_ADDRESS = "13994 Siena Loop"
ASK = 1_195_000
LIVING_SF = 2_623
TOTAL_SF = 3_548

# 2025 tax bill, parcel 588502359. CDD is inside the $13,012.60, not extra.
SELLER_TAX_BILL = 13_012.60
AD_VALOREM = 9_244.01
NON_AD_VALOREM = 3_768.59
CDD_OM = 3_165.87
CDD_DEBT = 330.66
FIRE_NON_AD = 272.06
SCHOOL_MILLS = 6.304
NONSCHOOL_MILLS = 7.856
TOTAL_MILLS = 14.160
HOMESTEAD_SCHOOL = 25_000
HOMESTEAD_NONSCHOOL = 50_000
MARKET_VALUE = 713_184
ASSESSED_VALUE = 692_095
PRIOR_SALE = 445_000

# Planning ranges, not contractor bids.
ROOF_LOW, ROOF_HIGH = 40_000, 80_000
HVAC_LOW, HVAC_HIGH = 8_000, 16_000

# Comps. price is sold price for closed sales and current ask for active listings.
# living_sf is public-record living area.
COMPS = [
    {
        "role": "Subject",
        "address": "13994 Siena Loop",
        "status": "Active",
        "as_of": "2026-10-23",
        "price": ASK,
        "original_ask": ASK,
        "beds": 3,
        "baths": "3",
        "living_sf": LIVING_SF,
        "year": 2006,
        "lot_acres": 0.23,
        "view": "Golf and lake",
        "updates": "Agent 23 Oct 2026: roof 20 years old, HVAC 2024 and HVAC 2017, pool heater 2020. Water heater still undated.",
        "source": "MLS A4704244",
    },
    {
        "role": "Active",
        "address": "13978 Siena Loop",
        "status": "Under contract, backups",
        "as_of": "2026-10-23",
        "price": 899_000,
        "original_ask": 899_000,
        "beds": 3,
        "baths": "3",
        "living_sf": 2_673,
        "year": 2004,
        "lot_acres": 0.21,
        "view": "Golf and lake",
        "updates": "4-ton 16 SEER AC replaced Apr 2026; softener; new pool coping and tile",
        "source": "MLS A4705315",
    },
    {
        "role": "Active",
        "address": "13853 Siena Loop",
        "status": "Active",
        "as_of": "2026-04-28",
        "price": 774_000,
        "original_ask": 779_000,
        "beds": 3,
        "baths": "2 + office",
        "living_sf": 2_321,
        "year": 2005,
        "lot_acres": None,
        "view": "Pond",
        "updates": "Recent HVAC and water heater; rescreened lanai; saltwater heated pool",
        "source": "MLS A4666855",
    },
    {
        "role": "Active",
        "address": "13860 Siena Loop",
        "status": "Active",
        "as_of": "2026-09-09",
        "price": 949_999,
        "original_ask": 1_056_000,
        "beds": 3,
        "baths": "3.5",
        "living_sf": 3_187,
        "year": None,
        "lot_acres": 0.21,
        "view": "Country club",
        "updates": "Lennox AC 2024; water heater 2025. Original ask inferred from a reported 5.4% cut to $999,000",
        "source": "MLS TB8526072",
    },
    {
        "role": "Active",
        "address": "13911 Siena Loop",
        "status": "Active",
        "as_of": "2026-08-20",
        "price": 995_000,
        "original_ask": 1_295_000,
        "beds": 4,
        "baths": "3.5",
        "living_sf": 3_216,
        "year": 2004,
        "lot_acres": 0.27,
        "view": "Lake",
        "updates": "AC 2024; pool heater 2023; 3-car garage; outdoor kitchen. Remarks say 3–4 bedrooms because of a media room. Listed 16 Jan 2026",
        "source": "MLS A4678185",
    },
    {
        "role": "Sold",
        "address": "13828 Siena Loop",
        "status": "Sold 2026-06-01",
        "as_of": "2026-06-01",
        "price": 799_000,
        "original_ask": 820_000,
        "beds": 3,
        "baths": "2 + office",
        "living_sf": 2_311,
        "year": 2003,
        "lot_acres": 0.18,
        "view": "Golf, rear view",
        "updates": "Brand-new tile roof; new pool heater; cage rescreened and repainted; outdoor kitchen",
        "source": "MLS A4687316",
    },
    {
        "role": "Sold",
        "address": "13804 Siena Loop",
        "status": "Sold 2026-06-12",
        "as_of": "2026-06-12",
        "price": 790_000,
        "original_ask": None,
        "beds": 3,
        "baths": "2 + office",
        "living_sf": 2_319,
        "year": 2005,
        "lot_acres": 0.35,
        "view": "Pond, near golf",
        "updates": "Renovated kitchen, quartzite, outdoor kitchen, heated pool. Oversized cul-de-sac lot",
        "source": "MLS A4691647",
    },
    {
        "role": "Sold",
        "address": "13987 Siena Loop",
        "status": "Sold week of 2026-08-03",
        "as_of": "2026-08-07",
        "price": 760_000,
        "original_ask": None,
        "beds": 3,
        "baths": "2",
        "living_sf": 2_289,
        "year": 2003,
        "lot_acres": None,
        "view": "Siena Loop",
        "updates": "Pool. Prior sale $810,000 in 2023, so this sale was a loss",
        "source": "Your Observer, 18 Aug 2026",
    },
    {
        "role": "Sold",
        "address": "13876 Siena Loop",
        "status": "Sold 2026-04-30",
        "as_of": "2026-04-30",
        "price": 775_000,
        "original_ask": 849_000,
        "beds": 3,
        "baths": "3.5",
        "living_sf": 2_610,
        "year": 2004,
        "lot_acres": 0.21,
        "view": "Siena Loop",
        "updates": "Listed 20 Oct 2025 at $849,000. Closest sold size to the subject",
        "source": "Stellar MLS via Homefinder",
    },
    {
        "role": "Sold",
        "address": "13861 Siena Loop",
        "status": "Sold 2026-03-19",
        "as_of": "2026-03-19",
        "price": 610_000,
        "original_ask": 749_000,
        "beds": 3,
        "baths": "2",
        "living_sf": 2_134,
        "year": 2003,
        "lot_acres": 0.25,
        "view": "Water",
        "updates": "HVAC 2023; pool pump, heater, and pebble surface 2025-26",
        "source": "MLS A4668432",
    },
    {
        "role": "Sold",
        "address": "13844 Siena Loop",
        "status": "Sold 2026-01-29",
        "as_of": "2026-01-29",
        "price": 619_425,
        "original_ask": 699_000,
        "beds": 2,
        "baths": "2",
        "living_sf": 2_134,
        "year": 2003,
        "lot_acres": None,
        "view": "Siena Loop",
        "updates": "Pool. Smaller 2-bedroom plan",
        "source": "MLS A4671692",
    },
]


def price_per_sf(price: int, living_sf: int) -> float:
    return price / living_sf


def sold_comps() -> list[dict]:
    return [c for c in COMPS if c["role"] == "Sold"]


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def sold_median_ppsf() -> float:
    return median([price_per_sf(c["price"], c["living_sf"]) for c in sold_comps()])


def twin_implied_value() -> float:
    """13978 contract ask applied to the subject's living area."""
    twin = next(c for c in COMPS if c["address"].startswith("13978"))
    return price_per_sf(twin["price"], twin["living_sf"]) * LIVING_SF


def non_homestead_tax(price: float) -> float:
    return price * TOTAL_MILLS / 1000 + NON_AD_VALOREM


def homestead_tax(price: float) -> float:
    school = max(price - HOMESTEAD_SCHOOL, 0) * SCHOOL_MILLS / 1000
    county = max(price - HOMESTEAD_NONSCHOOL, 0) * NONSCHOOL_MILLS / 1000
    return school + county + NON_AD_VALOREM


# Listing-agent ages reported 23 Oct 2026: roof 20 years, HVAC 2024 and 2017, pool heater 2020.
OFFER = 850_000
SUPPORTED = 880_000
CEILING = 910_000


def desk_range() -> dict[str, int]:
    """Offer, supported value, and ceiling after the listing agent's equipment ages."""
    return {
        "offer": OFFER,
        "supported": SUPPORTED,
        "ceiling": CEILING,
    }


HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True, name="Calibri", size=11)
SUBJECT_FILL = PatternFill("solid", fgColor="F4B183")
SOLD_FILL = PatternFill("solid", fgColor="E2EFDA")
ACTIVE_FILL = PatternFill("solid", fgColor="DDEBF7")
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Border(
    left=Side(style="thin", color="D9D9D9"),
    right=Side(style="thin", color="D9D9D9"),
    top=Side(style="thin", color="D9D9D9"),
    bottom=Side(style="thin", color="D9D9D9"),
)
WRAP = Alignment(wrap_text=True, vertical="center")
MONEY = '"$"#,##0'
MONEY_C = '"$"#,##0.00'
PPSF = '"$"#,##0.00'
NUM = '#,##0'
PCT = '0.0%'


def _header(ws, row: int, titles: list[str]) -> None:
    for col, title in enumerate(titles, 1):
        cell = ws.cell(row, col, title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = THIN
    ws.row_dimensions[row].height = 32
    ws.auto_filter.ref = f"A{row}:{get_column_letter(len(titles))}{row}"
    ws.freeze_panes = f"A{row + 1}"


def _widths(ws, widths: list[float]) -> None:
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width


def _write_kv(ws, rows: list[tuple], label_width: float = 38) -> None:
    ws.column_dimensions["A"].width = label_width
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 88
    for i, (label, value, note) in enumerate(rows, 1):
        a = ws.cell(i, 1, label)
        b = ws.cell(i, 2, value)
        c = ws.cell(i, 3, note)
        a.font = Font(bold=True, name="Calibri")
        a.alignment = WRAP
        b.alignment = WRAP
        c.alignment = WRAP
        for col in (1, 2, 3):
            ws.cell(i, col).border = THIN
        ws.row_dimensions[i].height = 32 if note else 18


def build_workbook(path: Path) -> Path:
    wb = Workbook()

    # --- How to use ---
    how = wb.active
    how.title = "How to use"
    how["A1"] = "Lakewood Ranch home comparison"
    how["A1"].font = Font(bold=True, size=16, name="Calibri", color="1F4E79")
    how.merge_cells("A2:A8")
    how["A2"] = (
        "Add the next house as a new row on the Comps sheet. Set Role to Subject, Active, or Sold. "
        "Price per living sq ft and the gap versus 13994 calculate themselves. "
        "Yellow cells on Valuation are the only inputs. "
        "Use living area, never total under-roof area. "
        "13394 Siena Loop is not a parcel; this file analyzes 13994 Siena Loop. "
        "Pulled 23 Oct 2026 (Pacific). Desk comparison, not an appraisal."
    )
    how["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    how.column_dimensions["A"].width = 120
    how.row_dimensions[2].height = 90

    # --- Subject ---
    sub = wb.create_sheet("Subject")
    subject_rows = [
        ("Address analyzed", SUBJECT_ADDRESS, "User typed 13394. No Manatee parcel uses that number. Tax roll also spells the street SIENNA."),
        ("MLS", "A4704244", "Stellar / My Florida Regional. Listed 4 Sep 2026 by Katina and Kenneth Shanahan, Coldwell Banker."),
        ("Status as of 23 Oct 2026", "Active, 49 days, no cut", "Zachos snapshot updated 23 Oct 2026. An open house was scheduled 18 Oct 2026, 1–4pm."),
        ("Ask", ASK, "No price reduction since the list date."),
        ("Living area", LIVING_SF, "Public-record living area. This is the denominator for every $/sf figure in this file."),
        ("Total building area", TOTAL_SF, "Garage and lanai are inside this number. Ask divided by 3,548 is about $337/sf and is not comparable."),
        ("Ask per living sq ft", round(ASK / LIVING_SF, 2), "1,195,000 / 2,623."),
        ("Beds / baths", "3 / 3", "The third bath serves the office and the pool. Guest bedrooms share one bath. Office is not a fourth bedroom."),
        ("Year built / stories", "2006 / one story", "Stucco on slab. Builder not named in the current MLS remarks."),
        ("Lot", "0.23 acres / 9,810 sf", "Lot 47, Block A. Legal: Country Club Village subphase R, Siena, and subphase S, Mizner Reserve."),
        ("Parcel", "588502359", "Manatee County. Zoning A/WPE. Flood zone X on the Coldwell Banker detail page."),
        ("Owners of record", "Timothy P. and Shannon L. Moriarty", "Homestead and Additional Homestead. Mortgage escrow is PHH. Public tax roll."),
        ("Last sale", PRIOR_SALE, "Sold 21 May 2020, prior MLS A4436936. Listed 24 May 2019 at $540,000 and cut five times."),
        ("2025 market / assessed", f"{MARKET_VALUE} / {ASSESSED_VALUE}", "Save Our Homes keeps assessed value under market value. Market value is still far under the ask."),
        ("2025 tax bill", SELLER_TAX_BILL, "Paid 1 Dec 2025 from escrow, $12,492.10 after discount. Bill includes the CDD."),
        ("Of which ad valorem", AD_VALOREM, "Millage 14.160 combined. School exemption $25,000. Non-school exemption $50,722."),
        ("Of which non-ad valorem", NON_AD_VALOREM, f"CDD 5 operations ${CDD_OM:,.2f}, CDD debt ${CDD_DEBT:,.2f}, East Manatee fire ${FIRE_NON_AD:,.2f}."),
        ("MLS association fee", 135, "Per year, Lakewood Ranch Town Hall. This is not the Siena maintenance fee. Neighbors disclose $175–$188 per month."),
        ("Roof", "Tile, 20 years old", "Listing agent, 23 Oct 2026. On a 2006 house this is the original roof. Underlayment is the insurance issue. Planning range to replace tile is $40,000–$80,000, not a bid."),
        ("HVAC", "2024 and 2017", "Listing agent, 23 Oct 2026. Two systems, replaced on different dates. The 2017 unit is mid-life. Tonnage and zones are still unknown."),
        ("Pool", "Heater 2020. Surface and cage undated.", "The pool, spa, and outdoor kitchen were already in the May 2019 remarks. The heater date does not date the surface or the screen cage."),
        ("Orientation", "Front faces east", "Photo captions describe a west-facing lanai and sunsets. Consistent with a rear-west plan."),
        ("Schools", "Willis / Nolan / Lakewood Ranch High", "Public assignment. Confirm boundaries before relying on them."),
    ]
    _write_kv(sub, subject_rows)
    sub.cell(4, 2).number_format = MONEY
    sub.cell(5, 2).number_format = NUM
    sub.cell(6, 2).number_format = NUM
    sub.cell(7, 2).number_format = PPSF
    sub.cell(13, 2).number_format = MONEY
    sub.cell(15, 2).number_format = MONEY_C
    sub.cell(16, 2).number_format = MONEY_C
    sub.cell(17, 2).number_format = MONEY_C
    sub.cell(18, 2).number_format = MONEY
    sub.auto_filter.ref = "A1:C23"
    sub.freeze_panes = "A2"
    sub.page_setup.orientation = "landscape"
    sub.page_setup.fitToPage = True
    sub.page_setup.fitToWidth = 1
    sub.page_setup.fitToHeight = 1
    sub.sheet_properties.pageSetUpPr.fitToPage = True
    sub.oddHeader.left.text = "13994 Siena Loop desk file"
    sub.oddFooter.right.text = "Page &P of &N"
    sub.print_title_rows = "1:1"
    sub.page_setup.paperSize = sub.PAPERSIZE_TABLOID

    # --- Comps ---
    comps = wb.create_sheet("Comps")
    comp_headers = [
        "Role",
        "Address",
        "Status",
        "As of",
        "Price",
        "Original ask",
        "Beds",
        "Baths",
        "Living sf",
        "Year",
        "Lot acres",
        "View",
        "$ / living sf",
        "Gap vs subject $",
        "Gap vs subject $/sf",
        "Subject premium",
        "Updates",
        "Source",
    ]
    _header(comps, 1, comp_headers)
    for r, comp in enumerate(COMPS, 2):
        values = [
            comp["role"],
            comp["address"],
            comp["status"],
            comp["as_of"],
            comp["price"],
            comp["original_ask"],
            comp["beds"],
            comp["baths"],
            comp["living_sf"],
            comp["year"],
            comp["lot_acres"],
            comp["view"],
            f'=IF(I{r}="","",E{r}/I{r})',
            f'=IF(E{r}="","",$E$2-E{r})',
            f'=IF(M{r}="","",$M$2-M{r})',
            f'=IF(OR(E{r}="",E{r}=0),"",($E$2-E{r})/E{r})',
            comp["updates"],
            comp["source"],
        ]
        fill = {"Subject": SUBJECT_FILL, "Sold": SOLD_FILL, "Active": ACTIVE_FILL}[comp["role"]]
        for c, value in enumerate(values, 1):
            cell = comps.cell(r, c, value)
            cell.fill = fill
            cell.border = THIN
            cell.alignment = WRAP
            cell.font = Font(name="Calibri", size=10, bold=(comp["role"] == "Subject"))
        comps.cell(r, 5).number_format = MONEY
        comps.cell(r, 6).number_format = MONEY
        comps.cell(r, 9).number_format = NUM
        comps.cell(r, 13).number_format = PPSF
        comps.cell(r, 14).number_format = MONEY
        comps.cell(r, 15).number_format = PPSF
        comps.cell(r, 16).number_format = PCT
        comps.row_dimensions[r].height = 36
    last = 1 + len(COMPS)
    comps.cell(last + 2, 1, "Sold median $/sf")
    comps.cell(last + 2, 2).number_format = PPSF
    comps.cell(last + 2, 1).font = Font(bold=True)
    comps.cell(last + 3, 1, "Sold count")
    comps.cell(last + 3, 2, f'=COUNTIF(A2:A{last},"Sold")')
    comps.cell(last + 2, 2).fill = INPUT_FILL
    _widths(
        comps,
        [12, 22, 28, 14, 14, 16, 8, 12, 12, 8, 12, 18, 14, 18, 18, 16, 62, 32],
    )
    comps.auto_filter.ref = f"A1:R{last}"
    comps.freeze_panes = "C2"
    comps.auto_filter.ref = f"A1:R{last}"
    comps.page_setup.orientation = "landscape"
    comps.page_setup.fitToPage = True
    comps.page_setup.fitToWidth = 1
    comps.page_setup.fitToHeight = 1
    comps.page_setup.paperSize = comps.PAPERSIZE_TABLOID
    comps.sheet_properties.pageSetUpPr.fitToPage = True
    comps.print_title_rows = "1:1"
    comps.oddHeader.left.text = "Siena Loop comps — living area only"
    comps.oddFooter.right.text = "Page &P of &N"
    comps.page_setup.horizontalCentered = True
    role_check = DataValidation(type="list", formula1='"Subject,Active,Sold"', allow_blank=False)
    role_check.error = "Use Subject, Active, or Sold"
    role_check.errorTitle = "Role"
    comps.add_data_validation(role_check)
    role_check.add(f"A2:A{last + 20}")

    # Named-style median using AGGREGATE so Excel does not need a CSE array.
    # AGGREGATE 16 is MEDIAN, option 6 ignores errors. Cannot filter by role directly.
    # Helper column S holds sold $/sf only.
    comps.cell(1, 19, "Sold $/sf helper")
    comps.cell(1, 19).font = HEADER_FONT
    comps.cell(1, 19).fill = HEADER_FILL
    for r in range(2, last + 1):
        comps.cell(r, 19, f'=IF(A{r}="Sold",M{r},NA())')
        comps.cell(r, 19).number_format = PPSF
    comps.column_dimensions["S"].hidden = True
    comps.cell(last + 2, 2, f"=AGGREGATE(16,6,S2:S{last})")

    chart = BarChart()
    chart.type = "bar"
    chart.style = 10
    chart.title = "Price per living square foot"
    chart.y_axis.title = "Address"
    chart.x_axis.title = "Dollars per living sq ft"
    data = Reference(comps, min_col=13, min_row=1, max_row=last)
    cats = Reference(comps, min_col=2, min_row=2, max_row=last)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.shape = 4
    chart.legend = None
    chart.y_axis.majorGridlines = None
    chart.height = 10
    chart.width = 18
    comps.add_chart(chart, "A16")

    # --- Valuation ---
    val = wb.create_sheet("Valuation")
    val["A1"] = "Desk value"
    val["A1"].font = Font(bold=True, size=16, color="1F4E79")
    val["A2"] = (
        "Yellow cells are inputs. Updated 23 Oct 2026 for the listing agent's ages: roof 20 years, HVAC 2024 and 2017, pool heater 2020. "
        "It is not an appraisal and it is not a prediction of the contract price."
    )
    val["A2"].alignment = Alignment(wrap_text=True)
    val.merge_cells("A2:C2")
    val.row_dimensions[2].height = 32

    labels = [
        (4, "Ask", ASK, "MLS A4704244"),
        (5, "Living sf", LIVING_SF, "Public record"),
        (6, "Ask $/sf", "=B4/B5", "Formula"),
        (7, "2026 sold median $/sf", round(sold_median_ppsf(), 2), "Six Siena Loop sales, Jan–Aug 2026"),
        (8, "13978 contract ask", 899_000, "Same beds, 3 baths, office, golf and lake. Under contract, backups, as of 23 Oct 2026"),
        (9, "13978 living sf", 2673, "MLS A4705315"),
        (10, "13978 $/sf", "=B8/B9", "Formula"),
        (11, "Subject sized at 13978 $/sf", "=B10*B5", "What this house costs if it sells at the twin's ask rate"),
        (12, "Dollars above that twin", "=B4-B11", "Ask minus the twin-sized value"),
        (13, "Opening offer", OFFER, "Start here. The roof is confirmed 20 years old, so the offer leaves room for a roof credit."),
        (14, "Supported value", SUPPORTED, "About the 13978 contract rate on this living area. The 2024 HVAC offsets part of the known roof. It does not support a premium."),
        (15, "Ceiling", CEILING, "Only with an affordable insurance binder and a roof report that does not require immediate replacement."),
        (16, "Ask vs supported", "=B4/B14-1", "Percent the ask sits above the supported value"),
        (17, "Dollars above supported", "=B4-B14", "Gap between the ask and the supported value"),
        (18, "2020 purchase", PRIOR_SALE, "21 May 2020. Ask is 2.69 times that price"),
        (19, "Ask / 2020 price", "=B4/B18", "Formula"),
        (20, "County 2025 market value", MARKET_VALUE, "Tax roll. Lags renovations. Still the assessor's number, not the ask"),
        (21, "Ask / county market", "=B4/B20-1", "Formula"),
    ]
    val.column_dimensions["A"].width = 42
    val.column_dimensions["B"].width = 18
    val.column_dimensions["C"].width = 88
    for row, label, value, note in labels:
        val.cell(row, 1, label).font = Font(bold=True)
        val.cell(row, 1).alignment = WRAP
        cell = val.cell(row, 2, value)
        cell.alignment = WRAP
        val.cell(row, 3, note).alignment = WRAP
        for col in (1, 2, 3):
            val.cell(row, col).border = THIN
        val.row_dimensions[row].height = 30
    for row in (4, 8, 11, 12, 13, 14, 15, 17, 18, 20):
        val.cell(row, 2).number_format = MONEY
    for row in (6, 7, 10):
        val.cell(row, 2).number_format = PPSF
    val.cell(5, 2).number_format = NUM
    val.cell(9, 2).number_format = NUM
    for row in (16, 19, 21):
        val.cell(row, 2).number_format = PCT
    for row in (7, 13, 14, 15):
        val.cell(row, 2).fill = INPUT_FILL

    val["A23"] = "Why the ask does not clear"
    val["A23"].font = Font(bold=True, size=14, color="1F4E79")
    val.merge_cells("A24:C27")
    val["A24"] = (
        "Six 2026 sales on this loop closed from $286 to $346 per living foot, median about $314. "
        "The four active neighbors are $298 to $336 per foot. The closest product, 13978, has the same bedroom count, "
        "three baths, an office, and a golf-and-lake lot, plus a dated April 2026 air conditioner, and it found a buyer at a $899,000 ask. "
        "Sizing that rate to 2,623 feet is about $882,000. "
        "13911 started at $1,295,000 in January 2026, has been cut to $995,000, and was still active in August with more bedrooms, more baths, and a 2024 air conditioner. "
        "This house's own 2019 campaign listed at $540,000 and sold at $445,000. "
        "The current remarks sell a remodel. The May 2019 remarks already advertised the pool, spa, outdoor kitchen, tile floors, 48-inch cabinets, granite island, and the office bath. "
        "Quartz, new cabinet claims, bath glass, a wine bar, an electric fireplace, and a softener can support a finish premium. They do not support $456 per foot. "
        "On 23 Oct 2026 the listing agent dated the roof at 20 years old, one air conditioner at 2024, the second air conditioner at 2017, and the pool heater at 2020. "
        "The 2024 system and the 2020 heater remove the all-original mechanicals case. The 20-year roof removes the $1,030,000 case. Supported value is $880,000. Open at $850,000. Do not exceed $910,000."
    )
    val["A24"].alignment = Alignment(wrap_text=True, vertical="top")
    val.row_dimensions[24].height = 30
    val.row_dimensions[25].height = 30
    val.row_dimensions[26].height = 30
    val.row_dimensions[27].height = 30
    val.page_setup.orientation = "landscape"
    val.page_setup.fitToPage = True
    val.page_setup.fitToWidth = 1
    val.page_setup.fitToHeight = 1
    val.page_setup.paperSize = val.PAPERSIZE_TABLOID
    val.sheet_properties.pageSetUpPr.fitToPage = True
    val.print_title_rows = "1:1"
    val.oddFooter.right.text = "Page &P of &N"
    val.oddHeader.left.text = "13994 Siena Loop valuation"

    # --- Costs ---
    costs = wb.create_sheet("Carrying costs")
    costs["A1"] = "Buyer carrying cost versus the seller's bill"
    costs["A1"].font = Font(bold=True, size=16, color="1F4E79")
    cost_headers = ["Item", "Seller today", "Buyer at ask, year 1", "Buyer at mid value, year 1", "Notes"]
    for c, title in enumerate(cost_headers, 1):
        cell = costs.cell(3, c, title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = WRAP
    # Inputs
    costs["A4"] = "Price used"
    costs["B4"] = 0
    costs["C4"] = "=Valuation!B4"
    costs["D4"] = "=Valuation!B14"
    costs["E4"] = "Seller price cell is blank on purpose. The seller already owns the house."
    costs["A5"] = "Ad valorem, no homestead"
    costs["B5"] = AD_VALOREM
    costs["C5"] = f"=C4*{TOTAL_MILLS}/1000"
    costs["D5"] = f"=D4*{TOTAL_MILLS}/1000"
    costs["E5"] = "Year-of-purchase estimate if the buyer does not have homestead on 1 Jan. Seller figure is the actual 2025 ad valorem, after homestead and Save Our Homes."
    costs["A6"] = "Non-ad valorem"
    costs["B6"] = NON_AD_VALOREM
    costs["C6"] = NON_AD_VALOREM
    costs["D6"] = NON_AD_VALOREM
    costs["E6"] = "2025 bill. CDD operations can move. Proposed FY2026/27 Siena CDD total is $3,781.92 versus $3,496.53 billed."
    costs["A7"] = "Tax bill"
    costs["B7"] = "=B5+B6"
    costs["C7"] = "=C5+C6"
    costs["D7"] = "=D5+D6"
    costs["E7"] = "Seller combined bill was $13,012.60. Early-pay discount made the December draft $12,492.10."
    costs["A8"] = "Homestead tax, year 2"
    costs["B8"] = SELLER_TAX_BILL
    costs["C8"] = f"=MAX(C4-{HOMESTEAD_SCHOOL},0)*{SCHOOL_MILLS}/1000+MAX(C4-{HOMESTEAD_NONSCHOOL},0)*{NONSCHOOL_MILLS}/1000+C6"
    costs["D8"] = f"=MAX(D4-{HOMESTEAD_SCHOOL},0)*{SCHOOL_MILLS}/1000+MAX(D4-{HOMESTEAD_NONSCHOOL},0)*{NONSCHOOL_MILLS}/1000+D6"
    costs["E8"] = "Assumes a new homestead and no portability. A buyer who ports a Florida homestead cap pays less. School mills 6.304. Other mills 7.856."
    costs["A9"] = "Town Hall fee"
    costs["B9"] = 135
    costs["C9"] = 135
    costs["D9"] = 135
    costs["E9"] = "The only association dollar in this MLS. Annual."
    costs["A10"] = "Siena maintenance, planning"
    costs["B10"] = 186 * 12
    costs["C10"] = "=B10"
    costs["D10"] = "=B10"
    costs["E10"] = "Not on this listing. 13828 disclosed $186 per month and 13804 disclosed $188. 13853 disclosed $175. Confirm on the estoppel."
    costs["A11"] = "Insurance"
    costs["B11"] = "Unknown"
    costs["C11"] = "Quote before offer"
    costs["D11"] = "Quote before offer"
    costs["E11"] = "A 2006 tile roof with unknown underlayment is the variable. Get a binder quote, not a rule-of-thumb."
    costs["A12"] = "Club membership"
    costs["B12"] = "Optional"
    costs["C12"] = "Optional"
    costs["D12"] = "Optional"
    costs["E12"] = "2026 packet: Premier golf $110,000 initiation and $1,360 per month; Sports $15,000 and $430; Social $6,000 and $185. Not required to buy the house. Does not transfer with the deed."
    for row in range(4, 13):
        for col in range(1, 6):
            costs.cell(row, col).border = THIN
            costs.cell(row, col).alignment = WRAP
        costs.cell(row, 1).font = Font(bold=True)
        costs.row_dimensions[row].height = 36
    for row in (5, 6, 7, 8, 9, 10):
        for col in (2, 3, 4):
            if not (row == 4 and col == 2):
                costs.cell(row, col).number_format = MONEY_C
    costs["C4"].number_format = MONEY
    costs["D4"].number_format = MONEY
    costs["B4"].number_format = MONEY
    _widths(costs, [34, 22, 26, 30, 78])
    costs.freeze_panes = "A4"
    costs.page_setup.orientation = "landscape"
    costs.page_setup.fitToPage = True
    costs.page_setup.fitToWidth = 1
    costs.page_setup.fitToHeight = 1
    costs.page_setup.paperSize = costs.PAPERSIZE_TABLOID
    costs.sheet_properties.pageSetUpPr.fitToPage = True
    costs.print_title_rows = "3:3"
    costs.oddHeader.left.text = "Carrying costs"
    costs.oddFooter.right.text = "Page &P of &N"
    costs.row_dimensions[7].height = 32
    for col in (2, 3, 4):
        costs.cell(7, col).font = Font(bold=True)
        costs.cell(7, col).fill = WARN_FILL

    # --- Upgrades ---
    ups = wb.create_sheet("Upgrades")
    up_headers = ["Item", "What the 2026 listing says", "What the 2019 listing already said", "Treat as"]
    for c, title in enumerate(up_headers, 1):
        cell = ups.cell(1, c, title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = WRAP
    upgrade_rows = [
        ("Kitchen counters", "Quartz, large island", "Granite island", "Likely replaced since 2019. Real, limited dollars."),
        ("Cabinets", "New cabinetry and pantry", "48-inch cabinets and a walk-in pantry", "Verify they are new. The 2019 copy already sold tall cabinets."),
        ("Primary bath", "Frameless glass, double vanity, garden tub, private water closet", "Separate vanities, garden tub, spa shower", "Finish upgrade more than a new room."),
        ("Guest baths", "Both remodeled", "Three baths already, including the office bath", "Cosmetic unless permits show a rebuild."),
        ("Office bath", "Den bath doubles as the pool bath", "Office with its own private bathroom", "Same room, not an added bath."),
        ("Floors", "Tile", "18-inch tile in the main living area", "Already there in 2019."),
        ("Pool, spa, cage", "Heated pool and spa, screen enclosure", "Private pool, spa, and enclosed lanai", "Already there in 2019. Heater is 2020 per the agent. Surface and cage are still undated."),
        ("Outdoor kitchen", "Grill and outdoor kitchen", "Outdoor kitchen", "Already there in 2019."),
        ("Wine bar and fireplace", "Wine bar, electric fireplace", "Not in the 2019 remarks", "Cosmetic. An electric fireplace is not a gas fireplace."),
        ("Lighting and windows treatments", "Designer lighting and window treatments", "Not singled out in 2019", "Cosmetic. Not impact glass."),
        ("Water softener", "Whole-house softener listed as an appliance", "Not in the 2019 remarks", "Useful. Small dollars."),
        ("Closet", "Oversized custom organized closet", "Two walk-in closets", "Organization system, not added area."),
        ("Accent walls", "Distinctive accent walls", "Not in the 2019 remarks", "Paint and millwork."),
        ("Roof", "Agent: 20 years old", "Not described as new in 2019", "Original 2006 tile roof. Underlayment is the expensive item. Still get the certification."),
        ("Air conditioners", "Agent: one system 2024, second system 2017", "Not dated in 2019", "Two systems. The 2024 unit is current. The 2017 unit is mid-life. Ask which zone each serves."),
        ("Pool heater", "Agent: 2020", "Pool and spa already existed", "Serviceable. This date does not cover the pool surface or the screen cage."),
        ("Water heater", "Still not dated", "Not mentioned", "Still open. Typical life is inside the time since 2006."),
        ("Windows", "Blinds and treatments only", "Not described as impact", "No wind-mitigation credit is being claimed. Verify."),
        ("Public record renovation year", "Remarks say fully remodeled, no date", "Redfin shows a 2012 renovation year", "Do not treat 2012 as proven. Pull the permit file."),
    ]
    for r, row in enumerate(upgrade_rows, 2):
        for c, value in enumerate(row, 1):
            cell = ups.cell(r, c, value)
            cell.alignment = WRAP
            cell.border = THIN
            if c == 4 and value.startswith("Open"):
                cell.fill = WARN_FILL
        ups.row_dimensions[r].height = 32
    ups.auto_filter.ref = f"A1:D{1 + len(upgrade_rows)}"
    ups.freeze_panes = "A2"
    _widths(ups, [28, 55, 55, 62])
    ups.page_setup.orientation = "landscape"
    ups.page_setup.fitToPage = True
    ups.page_setup.fitToWidth = 1
    ups.page_setup.fitToHeight = 1
    ups.page_setup.paperSize = ups.PAPERSIZE_TABLOID
    ups.sheet_properties.pageSetUpPr.fitToPage = True
    ups.print_title_rows = "1:1"
    ups.oddHeader.left.text = "Upgrades versus the 2019 listing"
    ups.oddFooter.right.text = "Page &P of &N"
    ups.page_setup.horizontalCentered = True

    # --- Risks ---
    risks = wb.create_sheet("Risks")
    risk_headers = ["Risk", "Severity", "What is known", "What to require"]
    for c, title in enumerate(risk_headers, 1):
        cell = risks.cell(1, c, title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = WRAP
    risk_rows = [
        (
            "Price",
            "High",
            "Ask is $456/sf against a 2026 sold median near $314/sf and a same-view neighbor under contract at $336/sf.",
            "Do not write at the ask. Supported value is $880,000. Open at $850,000. Ceiling is $910,000.",
        ),
        (
            "Resale",
            "High",
            "13911 has been cut 23% from $1,295,000 and was still for sale at $995,000 with more house. 13987 sold in 2026 for less than its 2023 price.",
            "Underwrite an exit near the 2026 sold band, not near this ask.",
        ),
        (
            "Roof and insurance",
            "High",
            "Listing agent says the roof is 20 years old, so it is the original 2006 tile roof. 13828, which sold at $346/sf, led with a brand-new roof.",
            "Roof certification, 4-point, wind mitigation, and an insurance binder before the inspection period ends. Planning range to replace a tile roof of this size is $40,000–$80,000. That is not a bid.",
        ),
        (
            "Second HVAC and water heater",
            "Medium",
            "Listing agent: one air conditioner replaced in 2024, the second in 2017. Water heater is still undated.",
            "Confirm tonnage and which zone each system serves. Budget the 2017 unit for replacement later in the decade. Water heater planning range is $1,500–$3,000 if it is original.",
        ),
        (
            "Tax reset",
            "High",
            "Sellers have homestead. Assessed value is $692,095 and the bill is $13,013. A buyer does not inherit Save Our Homes.",
            "Use the Carrying costs sheet. At the ask, year-1 taxes are about $20,700 before any homestead.",
        ),
        (
            "Remodel story",
            "Medium",
            "2019 remarks already included the pool, spa, outdoor kitchen, tile, tall cabinets, granite, and office bath. Redfin shows a 2012 renovation field.",
            "Permit search for kitchen, bath, electric, and any wall changes. Unpermitted work is a loan and insurance problem.",
        ),
        (
            "HOA disclosure",
            "Medium",
            "MLS fee is $135 per year to Lakewood Ranch Town Hall. Siena is a 68-home maintenance-free village. Neighbors show about $175–$188 per month.",
            "Estoppel for both associations, what maintenance includes, and any special assessment.",
        ),
        (
            "Pool and cage",
            "Medium",
            "Listing agent dated the pool heater at 2020. Surface, pump, and the 2006 screen cage are still undated.",
            "Pool inspection. Resurface and rescreen are separate five-figure and four-figure jobs when they are due.",
        ),
        (
            "Three bedrooms",
            "Medium",
            "Office is a den with a pool bath, not a fourth bedroom. 13911 offers four bedrooms and 3.5 baths for $200,000 less ask.",
            "Price the bedroom count. The buyer pool at $1.2 million usually wants four bedrooms.",
        ),
        (
            "Golf lot",
            "Medium",
            "View is real and 13978 shows what buyers will pay for the same view. MLS waterfront flag is No. Balls, mowers, and chemicals come with the lot.",
            "Walk the lot on a play day. Do not pay a view premium 13978 did not get.",
        ),
        (
            "CDD",
            "Low",
            "Debt service is only $331 per year, so the bond is small. Operations are about $3,166 and the proposed FY2027 Siena total is $3,782.",
            "Read the CDD budget. The fee does not end when the small debt is gone.",
        ),
        (
            "Flood",
            "Low",
            "Listing detail says flood zone X. Lake is a view, not owned frontage. Reclaimed water irrigates the community.",
            "Still pull the FEMA map and ask about yard drainage after summer rain.",
        ),
        (
            "2006 construction screen",
            "Low",
            "No public record reviewed here ties this address to Chinese drywall. The build year sits in the 2001–2009 problem window.",
            "Look for blackened copper, a sulfur smell, and failed AC coils. Ordinary stucco and window-flashing leaks belong on the same inspection.",
        ),
        (
            "Club dues",
            "Low",
            "Membership is optional and Heritage Golf Group has owned the club since early 2024.",
            "If a membership matters, price it separately. Premier initiation in the 2026 packet is $110,000 plus $1,360 a month.",
        ),
    ]
    for r, row in enumerate(risk_rows, 2):
        for c, value in enumerate(row, 1):
            cell = risks.cell(r, c, value)
            cell.alignment = WRAP
            cell.border = THIN
        tone = row[1]
        risks.cell(r, 2).fill = {"High": PatternFill("solid", fgColor="F8CBAD"), "Medium": WARN_FILL, "Low": SOLD_FILL}[tone]
        risks.row_dimensions[r].height = 48
    risks.auto_filter.ref = f"A1:D{1 + len(risk_rows)}"
    risks.freeze_panes = "A2"
    _widths(risks, [28, 12, 70, 70])
    risks.page_setup.orientation = "landscape"
    risks.page_setup.fitToPage = True
    risks.page_setup.fitToWidth = 1
    risks.page_setup.fitToHeight = 1
    risks.page_setup.paperSize = risks.PAPERSIZE_TABLOID
    risks.sheet_properties.pageSetUpPr.fitToPage = True
    risks.print_title_rows = "1:1"
    risks.oddHeader.left.text = "Risks and hidden issues"
    risks.oddFooter.right.text = "Page &P of &N"
    sev = DataValidation(type="list", formula1='"High,Medium,Low"', allow_blank=False)
    risks.add_data_validation(sev)
    sev.add(f"B2:B{1 + len(risk_rows) + 10}")

    # --- Sources ---
    src = wb.create_sheet("Sources")
    src_headers = ["Fact", "Source", "Date used"]
    for c, title in enumerate(src_headers, 1):
        cell = src.cell(1, c, title)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    sources = [
        ("Ask, living area, tile roof, parcel, $135 Town Hall fee, $3,497 other assessment, flood zone X", "MLS A4704244 via Coldwell Banker, Berkshire Hathaway, and Zachos", "23 Oct 2026"),
        ("49 days online and listing text", "Zachos Realty listing snapshot", "Updated 23 Oct 2026"),
        ("2020 sale $445,000 and 2019 price cuts and remarks", "Redfin sale history, prior MLS A4436936; Coldwell Banker price history", "Pages read 23 Oct 2026"),
        ("2025 tax bill, homestead, CDD split, owners, market and assessed value", "Manatee County tax bill, parcel 588502359", "2025 bill, payment posted 1 Dec 2025"),
        ("13978 under contract at $899,000, AC dated April 2026", "SeaGlass and realestate.com.au reprint of MLS A4705315", "Updated 23 Oct 2026"),
        ("13853, 13860, 13911 asks and reductions", "William Raveis and Berkshire Hathaway listing pages", "23 Oct 2026"),
        ("13828 sold $799,000 on 2,311 sf with a new roof", "Coldwell Banker and Florida Real Estate Central, MLS A4687316", "Sold 1 Jun 2026"),
        ("13804 sold $790,000 on 2,319 sf", "Palm Paradise Realty, MLS A4691647", "Sold 12 Jun 2026"),
        ("13876 sold $775,000 on 2,610 sf", "Homefinder / Stellar MLS", "Sold 30 Apr 2026"),
        ("13861 sold $610,000 and 13844 sold $619,425", "BEX Realty MLS reprints", "19 Mar 2026 and 29 Jan 2026"),
        ("13987 sold $760,000, prior sale $810,000 in 2023", "Your Observer, Lakewood Ranch sales for 3–7 Aug 2026", "Published 18 Aug 2026"),
        ("Proposed FY2026/27 Siena CDD $3,781.92", "Lakewood Ranch CDD 5 budget-hearing notice, transcribed by Move With Momentum", "Hearing 17 Aug 2026, proposed"),
        ("Club initiation and dues", "Lakewood Ranch Golf & Country Club 2026 membership packet", "2026 packet"),
        ("Renovation year 2012 field", "Redfin public-record pane", "Unverified county field"),
    ]
    for r, row in enumerate(sources, 2):
        for c, value in enumerate(row, 1):
            cell = src.cell(r, c, value)
            cell.alignment = WRAP
            cell.border = THIN
        src.row_dimensions[r].height = 32
    _widths(src, [70, 78, 36])
    src.freeze_panes = "A2"
    src.auto_filter.ref = f"A1:C{1 + len(sources)}"
    src.page_setup.orientation = "landscape"
    src.page_setup.fitToPage = True
    src.page_setup.fitToWidth = 1
    src.page_setup.fitToHeight = 1
    src.page_setup.paperSize = src.PAPERSIZE_TABLOID
    src.sheet_properties.pageSetUpPr.fitToPage = True
    src.print_title_rows = "1:1"
    src.oddFooter.right.text = "Page &P of &N"

    # Print defaults for the cover sheet too.
    how.page_setup.orientation = "landscape"
    how.page_setup.fitToPage = True
    how.page_setup.fitToWidth = 1
    how.page_setup.fitToHeight = 1
    how.page_setup.paperSize = how.PAPERSIZE_TABLOID
    how.sheet_properties.pageSetUpPr.fitToPage = True
    how.oddFooter.right.text = "Page &P of &N"
    how.page_setup.horizontalCentered = True

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "real_estate" / "lakewood-ranch-homes.xlsx"
    build_workbook(out)
    print(out)


if __name__ == "__main__":
    main()
