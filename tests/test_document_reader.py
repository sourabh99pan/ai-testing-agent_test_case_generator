
from pathlib import Path

import pytest

from src.document_reader import read_pdf, extract_pages


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "documents" / "OHRM-User-Guide.pdf"


@pytest.mark.skipif(
    not PDF_PATH.exists(),
    reason="Place OHRM-User-Guide.pdf in the documents folder.",
)
def test_read_pdf_returns_page_text():
    pages = read_pdf(PDF_PATH)

    assert pages
    assert all("page_number" in page for page in pages)
    assert all("text" in page for page in pages)


@pytest.mark.skipif(
    not PDF_PATH.exists(),
    reason="Place OHRM-User-Guide.pdf in the documents folder.",
)
def test_extract_selected_pages():
    pages = extract_pages(PDF_PATH, start_page=10, end_page=11)

    assert pages
    assert all(10 <= page["page_number"] <= 11 for page in pages)


def test_read_pdf_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_pdf(tmp_path / "missing.pdf")
