"""Arrangement plan for 13994 Siena Loop.

Drawn from the household sketch (IMG_5997) and the listing photos.
Gemini 4 Argon read the sketch labels. Lengths are not measured.
The county living area is 2,623 sq ft. Garage, cage, pool, and spa
are outside that area.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_PDF = ROOT / "real_estate" / "13994-Siena-Loop-floor-plan.pdf"
OUT_SVG = ROOT / "real_estate" / "13994-Siena-Loop-floor-plan.svg"
DESKTOP_NAME = "13994 Siena Loop - floor plan.pdf"

# viewBox matches a letter page. y grows downward. Rear lanai is at the top.
W, H = 820, 1061


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class Plan:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, **attrs) -> None:
        extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>')

    def path(self, d: str, **attrs) -> None:
        extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        self.add(f'<path d="{d}" {extra}/>')

    def line(self, x1, y1, x2, y2, **attrs) -> None:
        extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {extra}/>')

    def text(self, x, y, content, size=13, weight=600, fill="#1c2830", anchor="middle", spacing=0) -> None:
        extra = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{extra}>'
            f"{_esc(content)}</text>"
        )

    def label(self, x, y, title, note="", size=14) -> None:
        self.text(x, y, title, size=size, weight=650, fill="#1a2b36")
        if note:
            self.text(x, y + size + 1, note, size=9, weight=500, fill="#5d6b76")

    def window(self, x1, y1, x2, y2) -> None:
        """A break in the wall with a glass line just inside."""
        self.line(x1, y1, x2, y2, stroke="#fbf8f2", stroke_width="10", stroke_linecap="square")
        self.line(x1, y1, x2, y2, stroke="#2c3d4a", stroke_width="2")
        # glass tick
        if abs(y2 - y1) < 2:
            self.line(x1, y1 + 5, x2, y2 + 5, stroke="#7f93a3", stroke_width="1.5")
        else:
            self.line(x1 + 5, y1, x2 + 5, y2, stroke="#7f93a3", stroke_width="1.5")

    def slider(self, x1, y1, x2, y2) -> None:
        self.line(x1, y1, x2, y2, stroke="#f4f7f8", stroke_width="11", stroke_linecap="square")
        self.line(x1, y1, x2, y2, stroke="#2f6f8f", stroke_width="3")

    def door(self, hinge_x, hinge_y, end_x, end_y) -> None:
        """Quarter-turn door from the closed line (hinge to end) swinging toward the room."""
        self.line(hinge_x, hinge_y, end_x, end_y, stroke="#fbf8f2", stroke_width="9")
        self.line(hinge_x, hinge_y, end_x, end_y, stroke="#2c3d4a", stroke_width="1.2")
        # small hinge mark
        self.add(
            f'<circle cx="{hinge_x}" cy="{hinge_y}" r="1.6" fill="#2c3d4a"/>'
        )


def build_svg() -> str:
    p = Plan()
    wall = 'stroke="#24323c" stroke-width="7" fill="none" stroke-linejoin="miter"'
    thin = 'stroke="#24323c" stroke-width="4" fill="none" stroke-linejoin="miter"'

    p.add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" '
        f'viewBox="0 0 {W} {H}" font-family="Inter, Liberation Sans, sans-serif">'
    )
    p.rect(0, 0, W, H, fill="#f7f4ee")

    # Header
    p.rect(0, 0, W, 58, fill="#1e3f5a")
    p.text(36, 28, "13994 Siena Loop", size=20, weight=650, fill="#ffffff", anchor="start")
    p.text(36, 46, "Lakewood Ranch  ·  arrangement plan  ·  25 Oct 2026, Pacific", size=11, weight=500, fill="#d5e2ec", anchor="start")
    p.text(784, 32, "Street at the bottom", size=11, weight=600, fill="#ffffff", anchor="end")
    p.text(784, 46, "Lanai and sunset at the top", size=10, weight=500, fill="#d5e2ec", anchor="end")

    # Cage, drawn first so the house sits on it.
    p.path(
        "M 46 168 L 46 78 L 760 78 L 760 430 L 620 430 L 530 500 L 480 500 "
        "L 480 400 L 316 400 L 316 168 Z",
        fill="#e3eddf",
        stroke="#8aa384",
        stroke_width="2",
        stroke_dasharray="5 4",
    )
    p.text(400, 96, "SCREEN CAGE  ·  LANAI", size=11, weight=650, fill="#3e6244", spacing=1.2)

    # Pool and spa
    p.path(
        "M 360 250 C 390 150, 470 130, 560 150 C 640 168, 670 230, 640 290 "
        "C 610 340, 520 330, 470 300 C 420 270, 390 300, 360 250 Z",
        fill="#8ec4dc",
        stroke="#3d7f9c",
        stroke_width="2",
    )
    p.text(520, 230, "POOL", size=13, weight=700, fill="#14384a")
    p.path(
        "M 640 118 L 700 108 L 748 140 L 736 190 L 678 196 L 632 160 Z",
        fill="#6aafcc",
        stroke="#2d6e8c",
        stroke_width="2",
    )
    p.text(690, 156, "SPA", size=12, weight=700, fill="#14384a")
    p.text(700, 100, "gravel bed", size=9, weight=500, fill="#3e6244")

    # Outdoor kitchen
    p.rect(328, 186, 58, 36, fill="#f7f1e4", stroke="#6d7a62", stroke_width="1.5")
    p.text(357, 208, "Grill", size=10, weight=600, fill="#3e6244")

    # House fill
    footprint = (
        "M 46 990 L 46 150 L 316 150 L 316 400 L 480 400 L 480 500 "
        "L 530 500 L 640 370 L 760 370 L 760 990 Z"
    )
    p.path(footprint, fill="#fffdf8", stroke="none")

    # Garage tone
    p.rect(500, 860, 260, 130, fill="#ece6db")
    # Primary bath tone
    p.rect(575, 705, 185, 155, fill="#f3f7f8")
    # Guest bath and pool bath
    p.rect(46, 735, 130, 80, fill="#f3f7f8")
    p.rect(150, 275, 142, 77, fill="#f3f7f8")

    # Exterior wall
    p.path(footprint, fill="none", stroke="#24323c", stroke_width="8", stroke_linejoin="miter")

    # Interior walls. Gaps are doors or open passages.
    walls = [
        # Office bottom, with a door gap near the wine bar.
        (46, 275, 118, 275),
        (156, 275, 316, 275),
        # Pool bath, between the office and the family room.
        (150, 275, 150, 352),
        (292, 275, 292, 352),
        (150, 352, 250, 352),
        (292, 352, 316, 352),
        # Family / kitchen, with a wide opening.
        (46, 510, 108, 510),
        (230, 510, 300, 510),
        # Kitchen / bed 3
        (46, 640, 246, 640),
        # Bed 3 / guest bath, door at the right end.
        (46, 735, 168, 735),
        # Guest bath / bed 2
        (46, 815, 150, 815),
        (176, 735, 176, 790),
        (176, 815, 176, 860),
        # Bed 2 and bedroom 3 side of the entry hall
        (246, 640, 246, 990),
        # Dining / laundry
        (430, 735, 430, 860),
        # Laundry
        (430, 755, 548, 755),
        (548, 735, 548, 860),
        (430, 860, 520, 860),
        # Garage top. The door into the house is the gap from x=520 to 575.
        (575, 860, 760, 860),
        # Primary bath
        (575, 700, 760, 700),
        (575, 735, 575, 860),
        # Closets and the hall between them
        (506, 545, 760, 545),
        (506, 545, 506, 655),
        (570, 545, 570, 700),
        (640, 545, 640, 700),
        (506, 700, 575, 700),
        # Pantry, inside the kitchen's lower right corner
        (236, 582, 296, 582),
        (296, 582, 296, 638),
        (236, 638, 296, 638),
        (236, 582, 236, 638),
        # Master west wall from the chamfer down to the closets
        (530, 500, 530, 545),
        # Dinette bay
        (316, 400, 316, 448),
        (480, 448, 480, 500),
    ]
    for x1, y1, x2, y2 in walls:
        p.line(x1, y1, x2, y2, stroke="#24323c", stroke_width="4", stroke_linecap="square")

    # Openings: sliders and windows erase a bit of wall and redraw glass.
    p.slider(316, 175, 316, 245)          # office to lanai
    p.slider(316, 365, 316, 440)          # family room to lanai
    p.slider(360, 400, 455, 400)          # dinette / sitting side to lanai
    p.window(480, 400, 480, 450)          # dinette corner window
    p.window(80, 150, 230, 150)           # office rear window
    p.window(46, 400, 46, 470)            # family room side windows, drawn as one bay
    p.window(655, 370, 735, 370)          # primary bedroom rear window
    # Angled French doors
    p.slider(548, 478, 612, 402)
    p.text(690, 400, "French doors", size=8, weight=650, fill="#2f6f8f")

    # Doors. Each leaf stays inside the room it swings into.
    p.door(168, 735, 168, 772)            # bedroom 3 into the hall
    p.door(176, 792, 214, 792)            # guest bath into the hall
    p.door(200, 815, 242, 815)            # bedroom 2 into the hall
    p.door(250, 582, 282, 582)            # pantry into the kitchen
    p.door(118, 275, 150, 248)            # office from the family room
    p.door(250, 275, 250, 312)            # pool bath into the office
    p.door(292, 318, 316, 318)            # pool bath to the lanai
    p.door(520, 860, 520, 828)            # garage into the laundry vestibule
    p.door(575, 735, 575, 778)            # primary bath from the hall
    p.door(688, 700, 724, 700)            # private toilet
    p.door(506, 655, 548, 655)            # closet hall from the living room
    # Front door
    p.line(300, 990, 360, 990, stroke="#fbf8f2", stroke_width="10")
    p.line(300, 990, 360, 990, stroke="#1e3f5a", stroke_width="3")
    p.text(330, 1006, "FRONT DOOR", size=8, weight=700, fill="#1e3f5a", spacing=0.6)

    # Light furniture, so the rooms match the photos and the sketch.
    def furn(x, y, w, h, label=""):
        p.rect(x, y, w, h, fill="none", stroke="#c3b8a6", stroke_width="1.25")
        if label:
            p.text(x + w / 2, y + h / 2 + 3, label, size=8, weight=500, fill="#9a8d7c")

    furn(168, 190, 28, 18)                # office chairs
    furn(70, 292, 36, 22)                 # pool-bath tub
    furn(96, 455, 70, 28)                 # couch
    furn(150, 358, 54, 12)                # fireplace
    furn(70, 545, 28, 40)                 # range
    furn(130, 548, 90, 42)                # island
    furn(200, 592, 28, 26)                # fridge
    furn(70, 760, 34, 22)                 # guest tub
    furn(78, 880, 70, 90)                 # bed 2
    furn(78, 655, 70, 60)                 # bed 3
    furn(300, 860, 28, 90)                # dining table
    furn(360, 560, 16, 16)
    furn(400, 600, 16, 16)                # sitting chairs
    furn(455, 790, 36, 28)                # washer
    furn(500, 790, 36, 28)                # dryer
    furn(600, 790, 70, 36)                # shower
    furn(690, 800, 22, 16)
    furn(718, 800, 22, 16)                # sinks
    furn(680, 735, 28, 22)                # angled tub hint
    furn(680, 400, 56, 74)                # primary bed
    furn(520, 575, 36, 90)                # left closet
    furn(660, 575, 80, 90)                # right closet

    # Room labels
    p.label(150, 210, "Office", "slider to the lanai")
    p.label(220, 316, "Pool bath", "door to office and lanai")
    p.label(150, 430, "Family room", "sketch: living room")
    p.text(78, 392, "Wine bar", size=8, weight=600, fill="#5d6b76", anchor="start")
    p.label(145, 575, "Kitchen", "island and pantry")
    p.label(266, 616, "Pantry", size=9)
    p.label(130, 690, "Bedroom 3", "")
    p.label(108, 778, "Guest bath", size=12)
    p.label(140, 900, "Bedroom 2", "")
    p.label(330, 800, "Dining", "front door")
    p.label(390, 530, "Living room", "sketch: sitting area")
    p.text(400, 478, "Dinette windows", size=9, weight=600, fill="#5d6b76")
    p.label(490, 805, "Laundry", size=12)
    p.label(630, 930, "Garage", "2 cars, door to the right of the entry")
    p.label(668, 785, "Primary bath", "shower, two sinks, angled tub")
    p.text(668, 748, "toilet room", size=8, weight=500, fill="#5d6b76")
    p.label(538, 640, "Closet", size=11)
    p.label(700, 640, "Closet", size=11)
    p.label(690, 470, "Primary bedroom", "angled doors to the lanai")

    # North arrow. Facing the house from the street, the garage is on the right,
    # and that right side is north. The arrow points to the right edge of the page.
    p.line(36, 1016, 86, 1016, stroke="#1e3f5a", stroke_width="1.6")
    p.path("M 86 1016 L 76 1011 L 76 1021 Z", fill="#1e3f5a")
    p.text(96, 1020, "N", size=12, weight=700, fill="#1e3f5a", anchor="start")
    p.text(118, 1020, "Garage side. The street is east. The lanai faces west.", size=10, weight=500, fill="#5d6b76", anchor="start")
    p.text(36, 1038, "Arrangement from the household sketch and the listing photos. Walls are not measured. County living area is 2,623 sq ft.", size=8.5, weight=500, fill="#4e5962", anchor="start")
    p.text(36, 1050, "The garage, cage, pool, and spa are outside that area. The sketch calls the fireplace room the living room and the blue-chair room the sitting area.", size=8.5, weight=500, fill="#4e5962", anchor="start")

    # Notes
    p.add("</svg>")
    body = "\n".join(p.parts)
    note = (
        "Arrangement from the household sketch and the listing photos. "
        "Walls are not measured, and this is not an appraisal sketch. "
        "County living area is 2,623 sq ft. The garage, cage, pool, and spa are outside that area. "
        "The sketch names the fireplace room “living room” and the blue-chair room “sitting area.” "
        "Those are the family room and the living room on this page. "
        "Three bedrooms, three baths, and the office. The pool bath is the office bath and also opens to the lanai."
    )
    return body, note


def build_html(svg: str, note: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: letter portrait; margin: 0.38in; }}
  html, body {{ margin: 0; padding: 0; background: #f7f4ee; }}
  body {{ font-family: Inter, "Liberation Sans", sans-serif; color: #1c2830; }}
  .page {{ width: 7.74in; margin: 0 auto; }}
  svg {{ width: 7.74in; height: auto; display: block; }}
</style>
</head>
<body>
  <div class="page">
    {svg}
  </div>
</body>
</html>
"""


def write_outputs(html_path: Path | None = None) -> tuple[str, str]:
    svg, note = build_svg()
    OUT_SVG.write_text(svg, encoding="utf-8")
    html = build_html(svg, note)
    target = html_path or Path("/tmp/siena-plan/floor-plan.html")
    target.write_text(html, encoding="utf-8")
    return svg, note


def write_pdf() -> None:
    import cairosvg

    cairosvg.svg2pdf(url=str(OUT_SVG), write_to=str(OUT_PDF))


def main() -> None:
    write_outputs()
    write_pdf()
    print(OUT_PDF)


if __name__ == "__main__":
    main()
