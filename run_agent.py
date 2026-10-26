
import json
from pathlib import Path

from agents.langgraph_test_case_workflow import build_workflow


def main():
    pdf_path = Path("documents/OHRM-User-Guide.pdf")

    # Ask the user which module to process.
    module_name = input(
        "Enter module name (login/pim/leave): "
    ).strip().lower()

    # Build the graph.
    workflow = build_workflow()

    initial_state = {
        "pdf_path": str(pdf_path),
        "module_name": module_name,
        "pages": [],
        "requirements": "",
        "test_cases": [],
        "validation_errors": [],
        "retry_count": 0,
        "requirements_list": [],
        "coverage_gaps": [],
        "coverage_report": {},
    }

    try:
        result = workflow.invoke(initial_state)

        # Save results separately for each module.
        output_path = Path("outputs") / f"{module_name}_test_cases.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            json.dumps(
                result["test_cases"],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(f"\nModule: {module_name}")
        print(f"Generated test cases: {len(result['test_cases'])}")
        print(f"Validation errors: {result['validation_errors']}")
        print(f"Saved to: {output_path}")

    except ValueError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
