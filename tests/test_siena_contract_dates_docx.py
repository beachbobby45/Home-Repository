"""The contract-date Word document follows the October 28 deposit date."""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from real_estate.build_siena_contract_dates_docx import DATES, build_docx


def _text(path: Path) -> str:
    doc = Document(path)
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.extend(cell.text for cell in row.cells)
    return "\n".join(parts)


def test_contract_dates_use_the_october_25_effective_date(tmp_path: Path):
    path = build_docx(tmp_path / "dates.docx")
    text = _text(path)
    assert "Sunday, October 25, 2026" in text
    assert "Wednesday, October 28, 2026" in text
    assert "Wednesday, November 4, 2026" in text
    assert "Friday, October 30, 2026" in text
    assert "Wednesday, November 18, 2026" in text
    assert "Tuesday, November 24, 2026" in text
    assert "Friday, November 27, 2026" in text
    assert "Monday, November 30, 2026" in text
    assert "Thursday, December 3, 2026" in text
    assert "Thursday, December 10, 2026" in text
    assert "$50,000" in text
    assert "$1,125,000" in text
    assert "$16,875" in text
    assert "$525 per quarter" in text
    assert "$186.25" in text
    assert "As Is rider is unchecked" in text
    assert "is not required" in text
    assert "The funding table was not changed." in text
    assert len(DATES) == 9
