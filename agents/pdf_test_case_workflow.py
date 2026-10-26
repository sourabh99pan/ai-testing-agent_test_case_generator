
from pathlib import Path

from src.document_reader import extract_module
from agents.test_case_generator import generate_test_cases


def generate_from_pdf(
    pdf_path: str | Path,
    module_name: str,
) -> list[dict]:
    pages = extract_module(pdf_path, module_name)

    if not pages:
        raise ValueError(
            f"No text found for module: {module_name}"
        )

    requirements = "\n\n".join(
        f"PDF page {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    return generate_test_cases(requirements)
