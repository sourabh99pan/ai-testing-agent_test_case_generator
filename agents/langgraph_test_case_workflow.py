
from typing import TypedDict
from src.document_reader import extract_module
from agents.test_case_generator import generate_test_cases
from langgraph.graph import StateGraph, START, END
import json
import re
from src.llm_client import get_llm
from pathlib import Path
from src.json_utils import parse_llm_json

class TestCaseState(TypedDict):
    pdf_path: str
    module_name: str
    pages: list[dict]
    requirements: str
    requirements_list: list[str]
    test_cases: list[dict]
    validation_errors: list[str]
    coverage_gaps: list[str]
    retry_count: int
    coverage_report: dict

def extract_document(state: TestCaseState) -> dict:
    pages = extract_module(
        state["pdf_path"],
        state["module_name"],
    )

    if not pages:
        raise ValueError(
            f"No text found for module: {state['module_name']}"
        )

    requirements = "\n\n".join(
        f"PDF page {page['page_number']}:\n{page['text']}"
        for page in pages
    )

    return {
        "pages": pages,
        "requirements": requirements,
    }


def generate_cases(state: TestCaseState) -> dict:
    test_cases = generate_test_cases(state["requirements"])

    return {"test_cases": test_cases}


def validate_cases(state: TestCaseState) -> dict:
    errors = []
    required_fields = {
        "test_case_id",
        "title",
        "preconditions",
        "steps",
        "expected_result",
        "priority",
        "assumptions",
    }

    test_cases = state["test_cases"]

    if not test_cases:
        errors.append("No test cases were generated.")

    seen_ids = set()

    for index, case in enumerate(test_cases, start=1):
        missing = required_fields - case.keys()

        if missing:
            errors.append(
                f"Test case {index} is missing fields: "
                f"{', '.join(sorted(missing))}"
            )

        case_id = case.get("test_case_id")

        if case_id and case_id in seen_ids:
            errors.append(f"Duplicate test case ID: {case_id}")

        if case_id:
            seen_ids.add(case_id)

    return {"validation_errors": errors}


def correct_cases(state: TestCaseState) -> dict:
    llm = get_llm()

    prompt = f"""
You are a QA test-case reviewer.

Fix the test cases to resolve the validation errors.
Preserve the original requirements and avoid inventing behavior.

Requirements:
{state["requirements"]}

Current test cases:
{json.dumps(state["test_cases"], indent=2)}

Validation errors:
{json.dumps(state["validation_errors"], indent=2)}

Return valid JSON only, using this structure:
{{
  "test_cases": [
    {{
      "test_case_id": "TC001",
      "title": "Test case title",
      "preconditions": [],
      "steps": [],
      "expected_result": "Expected result",
      "priority": "High",
      "assumptions": []
    }}
  ]
}}
"""

    response = llm.invoke(prompt)
    corrected = json.loads(response.content)

    return {
        "test_cases": corrected["test_cases"],
        "retry_count": state["retry_count"] + 1,
    }



MAX_RETRIES = 2


def route_after_validation(state: TestCaseState) -> str:
    if not state["validation_errors"]:
        return "finish"

    if state["retry_count"] < MAX_RETRIES:
        return "retry"

    return "finish"

def extract_requirements(state: TestCaseState) -> dict:
    llm = get_llm()

    prompt = f"""
You are a requirements analyst.

Identify distinct, explicit functional requirements
from the source text below.

Rules:
- Return only requirements supported by the source.
- Do not invent missing behavior.
- Exclude general descriptions that are not requirements.
- If the text contains no clear functional requirements,
  return an empty list.

Return valid JSON only in this format:
{{
  "requirements": [
    "Requirement 1",
    "Requirement 2"
  ]
}}

Source text:
{state["requirements"]}
"""

    response = llm.invoke(prompt)
    result = json.loads(response.content)

    return {"requirements_list": result["requirements"]}


def save_requirements(
    requirements: list[str],
    module_name: str,
) -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{module_name}_requirements.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            {"module": module_name, "requirements": requirements},
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Requirements saved to: {output_file}")

def save_requirements_node(state: TestCaseState) -> dict:
    save_requirements(
        state["requirements_list"],
        state["module_name"],
    )
    return {}

def analyze_requirement_coverage(state: TestCaseState) -> dict:
    llm = get_llm()

    prompt = f"""
You are a software testing coverage analyst.

Compare each requirement with the generated test cases.

Requirements:
{json.dumps(state["requirements_list"], indent=2)}

Test cases:
{json.dumps(state["test_cases"], indent=2)}

Rules:
- Evaluate every requirement individually.
- Mark a requirement as covered only if at least one test
  case meaningfully tests its expected behavior.
- Do not assume that a test case covers a requirement
  merely because they use similar words.
- Include matching test case IDs.
- If no test case covers a requirement, mark it uncovered.
- Do not invent requirements or test cases.

Return valid JSON only, using this structure:
{{
  "results": [
    {{
      "requirement": "Requirement text",
      "covered": true,
      "matching_test_case_ids": ["TC001"],
      "explanation": "Why the test case covers it"
    }}
  ]
}}
"""

    response = llm.invoke(prompt)
    print("LLM RAW RESPONSE:", repr(response.content))
    report = parse_llm_json(response.content)

    results = report["results"]
    total = len(state["requirements_list"])

    if len(results) != total:
        raise ValueError(
            f"Expected {total} coverage results, "
            f"but received {len(results)}."
        )

    covered_count = sum(
        1 for item in results if item["covered"]
    )

    coverage_percentage = (
        round(covered_count / total * 100, 2)
        if total else 0.0
    )

    coverage_gaps = [
        item["requirement"]
        for item in results
        if not item["covered"]
    ]

    coverage_report = {
        "module": state["module_name"],
        "total_requirements": total,
        "covered_requirements": covered_count,
        "uncovered_requirements": len(coverage_gaps),
        "coverage_percentage": coverage_percentage,
        "results": results,
        "coverage_gaps": coverage_gaps,
    }

    return {
        "coverage_report": coverage_report,
        "coverage_gaps": coverage_gaps,
    }

def save_coverage_node(state: TestCaseState) -> dict:
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_dir
        / f'{state["module_name"]}_coverage.json'
    )

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            state["coverage_report"],
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Coverage report saved to: {output_file}")
    print(
        "Requirement coverage: "
        f'{state["coverage_report"]["coverage_percentage"]}%'
    )
    print(
        "Uncovered requirements: "
        f'{state["coverage_report"]["uncovered_requirements"]}'
    )

    return {}


#def build_workflow(): defines a function that builds your LangGraph workflow.
def build_workflow():
    graph = StateGraph(TestCaseState) #creates the graph builder.

     # 1. Register all nodes
    graph.add_node("extract_document", extract_document) #adds tasks to the graph
    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("save_requirements", save_requirements_node)
    graph.add_node("generate_cases", generate_cases)
    graph.add_node("validate_cases", validate_cases)
    graph.add_node("correct_cases", correct_cases)
    graph.add_node("analyze_coverage", analyze_requirement_coverage)
    graph.add_node("save_coverage",save_coverage_node)

    # 2. Define the workflow sequence
    graph.add_edge(START, "extract_document")
    graph.add_edge("extract_document", "extract_requirements")
    graph.add_edge("extract_requirements", "save_requirements")
    graph.add_edge("save_requirements", "generate_cases")
    graph.add_edge("generate_cases", "validate_cases")
    graph.add_conditional_edges(
        "validate_cases",
        route_after_validation,
        {
            "finish": "analyze_coverage",
            "retry": "correct_cases",
        },
    )
    graph.add_edge("analyze_coverage", "save_coverage")
    graph.add_edge("save_coverage", END)    
    graph.add_edge("correct_cases", "validate_cases")

    return graph.compile() #compiles the graph into an executable workflow.
