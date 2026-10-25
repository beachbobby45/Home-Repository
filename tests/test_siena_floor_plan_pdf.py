"""The Siena arrangement plan names the rooms from the household sketch."""

import subprocess

from real_estate.build_siena_floor_plan import OUT_PDF, OUT_SVG, build_svg


def test_plan_names_the_rooms_and_keeps_the_sketch_names():
    svg, note = build_svg()
    for label in (
        "Office",
        "Pool bath",
        "Family room",
        "Living room",
        "Kitchen",
        "Bedroom 3",
        "Bedroom 2",
        "Guest bath",
        "Dining",
        "Laundry",
        "Primary bedroom",
        "Primary bath",
        "Garage",
        "POOL",
        "SPA",
        "French doors",
        "2,623",
    ):
        assert label in svg
    assert "not measured" in note
    assert "sitting area" in note
    assert OUT_SVG.read_text(encoding="utf-8") == svg


def test_pdf_is_one_page_with_the_room_names():
    info = subprocess.run(
        ["pdfinfo", str(OUT_PDF)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Pages:           1" in info.stdout
    text = subprocess.run(
        ["pdftotext", str(OUT_PDF), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for label in ("Family room", "Primary bedroom", "Garage", "Pool bath", "2,623"):
        assert label in text
