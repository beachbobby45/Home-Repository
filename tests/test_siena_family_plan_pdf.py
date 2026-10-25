"""The family funding plan states both paths through 2030."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from real_estate.build_siena_family_plan_pdf import (
    CASH_2027,
    GAP_2027,
    GAP_REFI,
    GAP_REFI_SS,
    GAP_STAY,
    GAP_STAY_SS,
    PI_65,
    PI_73,
    REFINANCE_BALANCE,
    TAX_2027,
    TAX_2028,
    TOTAL_2027,
    TOTAL_REFI,
    TOTAL_STAY,
    build_pdf,
)


def test_family_plan_uses_the_agreed_figures(tmp_path: Path):
    assert PI_73 == 6_170
    assert PI_65 == 5_002
    assert TAX_2027 == 1_530
    assert TAX_2028 == 1_465
    assert TOTAL_2027 == 9_397
    assert TOTAL_STAY == 9_332
    assert TOTAL_REFI == 8_164
    assert GAP_2027 == 4_297
    assert GAP_STAY == 4_232
    assert GAP_STAY_SS == 3_132
    assert GAP_REFI == 3_064
    assert GAP_REFI_SS == 1_964
    assert CASH_2027 == 51_564
    assert REFINANCE_BALANCE == 791_374

    pdf_path = build_pdf(tmp_path / "family.pdf")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf_path), "-"], text=True)
    flat = " ".join(text.split())
    assert "December 3, 2026" in flat
    assert "$1,125,000" in flat
    assert "$225,000" in flat
    assert "The rate stays at 7.3 percent" in flat
    assert "Refinance at the end of 2027" in flat
    assert "$9,397" in flat
    assert "$9,332" in flat
    assert "$8,164" in flat
    assert "$250,000" in flat
    assert "$150,000" in flat
    assert "$51,564" in flat
    assert "$116,052" in flat
    assert "$74,004" in flat
    assert "$148,785" in flat
    assert "$94,876" in flat
