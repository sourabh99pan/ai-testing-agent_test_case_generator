
import json
from pathlib import Path

from agents.langgraph_test_case_workflow import (
    build_workflow,
)


def test_langgraph_generates_login_cases():
    workflow = build_workflow()

    initial_state = {
        "pdf_path": "documents/OHRM-User-Guide.pdf",
        "module_name": "login",
        "pages": [],
        "requirements": "",
        "test_cases": [],
        "validation_errors": [],
        "retry_count": 0,
    }

    result = workflow.invoke(initial_state)

    assert result["test_cases"]
    assert result["validation_errors"] == []

    output_path = Path("outputs/langgraph_test_cases.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(
            result["test_cases"],
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nGenerated {len(result['test_cases'])} test cases.")
    print(f"Saved to: {output_path}")
