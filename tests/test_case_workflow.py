
import json
from pathlib import Path

from agents.pdf_test_case_workflow import generate_from_pdf


def test_generate_login_cases_from_pdf():
    pdf_path = Path("documents/OHRM-User-Guide.pdf")

    test_cases = generate_from_pdf(pdf_path, "login")

    assert len(test_cases) > 0

    output_path = Path("outputs/test_cases.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(test_cases, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nGenerated {len(test_cases)} test cases.")
    print(f"Saved to: {output_path}")
