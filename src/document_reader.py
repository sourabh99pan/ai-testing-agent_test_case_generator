
from pathlib import Path

import pymupdf  # PyMuPDF


# Printed page ranges from the OrangeHRM manual's table of contents.
MODULE_PAGES = {
    "login": (10, 11),
    "pim": (53, 73),
    "leave": (74, 82),
}

def read_pdf(file_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF, preserving page numbers.

    Returns:
        A list of dictionaries containing page number and text.
    """
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    pages = []

    with pymupdf.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "text": text,
                })

    if not pages:
        raise ValueError(f"No extractable text found in PDF: {pdf_path}")

    return pages


def extract_pages(
    file_path: str | Path,
    start_page: int,
    end_page: int,
) -> list[dict]:
    """Extract text from a 1-based PDF page range."""
    if start_page < 1 or end_page < start_page:
        raise ValueError("Invalid page range.")

    pages = []

    with pymupdf.open(file_path) as pdf:
        if end_page > len(pdf):
            raise ValueError("End page exceeds PDF page count.")

        for index in range(start_page - 1, end_page):
            text = pdf[index].get_text("text").strip()
            if text:
                pages.append({
                    "page_number": index + 1,
                    "text": text,
                })

    return pages


def extract_module(
    file_path: str | Path,
    module_name: str,
) -> list[dict]:
    """Extract the configured page range for a module."""
    key = module_name.strip().lower()

    if key not in MODULE_PAGES:
        available = ", ".join(MODULE_PAGES)
        raise ValueError(
            f"Unknown module '{module_name}'. Available: {available}"
        )

    start_page, end_page = MODULE_PAGES[key]
    print(
        f"Reading module '{key}': "
        f"PDF pages {start_page}-{end_page}"
    )

    return extract_pages(file_path, start_page, end_page)
