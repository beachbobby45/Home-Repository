"""The Siena brief PDF contains the desk conclusion and lands on the Desktop."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from real_estate.build_siena_pdf import DESKTOP_NAME, build_pdf, copy_to_desktop


def test_pdf_states_the_conclusion(tmp_path: Path):
    pdf_path = build_pdf(tmp_path / "brief.pdf")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf_path), "-"], text=True)
    assert "13994 Siena Loop" in text
    assert "13394" in text
    assert "$1,195,000" in text
    assert "$456" in text
    assert "$880,000" in text
    assert "$850,000" in text
    assert "$910,000" in text
    assert "20 years" in text
    assert "2017" in text
    assert "2024" in text
    assert "BLD2405-3790" in text
    assert "CMP-05031188" in text
    assert "CMP-05070213" in text
    assert "CMP-06011072" in text
    assert "None found" in text
    assert "no completed inspections" in text
    assert "13978 Siena Loop" in text
    assert "13853 Siena Loop" in text
    assert "13844 Siena Loop" in text
    assert "Save Our Homes" in text or "homestead" in text.lower()
    assert "not an appraisal" in text.lower()
    pages = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True)
    page_count = int(next(line.split(":", 1)[1] for line in pages.splitlines() if line.startswith("Pages:")))
    assert page_count >= 3


def test_desktop_copy_uses_the_readable_name(tmp_path: Path):
    pdf_path = build_pdf(tmp_path / "brief.pdf")
    dest = copy_to_desktop(pdf_path, tmp_path / "Desktop")
    assert dest.name == DESKTOP_NAME
    assert dest.stat().st_size > 20_000
