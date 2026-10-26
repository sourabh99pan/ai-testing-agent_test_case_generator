
import agents.langgraph_test_case_workflow as workflow_module


def test_langgraph_retries_after_validation_failure(monkeypatch):
    correction_calls = {"count": 0}

    # Return a simple extracted document without reading the PDF.
    def fake_extract_document(state):
        return {
            "pages": [],
            "requirements": "Users can log in with valid credentials.",
        }

    # Deliberately return an invalid test case.
    def fake_generate_cases(state):
        return {
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "Login test",
                }
            ]
        }

    # Simulate the correction node fixing the invalid test case.
    def fake_correct_cases(state):
        correction_calls["count"] += 1
        print("Correction node executed!")
        print("Retry count before correction:", state["retry_count"])

        return {
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "Successful login",
                    "preconditions": ["User has valid credentials"],
                    "steps": ["Enter credentials", "Click Login"],
                    "expected_result": "User is logged in",
                    "priority": "High",
                    "assumptions": [],
                }
            ],
            "retry_count": state["retry_count"] + 1,
        }

    # Replace real functions with predictable test doubles.
    monkeypatch.setattr(
        workflow_module, "extract_document", fake_extract_document
    )
    monkeypatch.setattr(
        workflow_module, "generate_cases", fake_generate_cases
    )
    monkeypatch.setattr(
        workflow_module, "correct_cases", fake_correct_cases
    )

    workflow = workflow_module.build_workflow()

    initial_state = {
        "pdf_path": "unused.pdf",
        "module_name": "login",
        "pages": [],
        "requirements": "",
        "test_cases": [],
        "validation_errors": [],
        "retry_count": 0,
    }

    print("Route function:", workflow_module.route_after_validation({
        "validation_errors": ["Missing fields"],
        "retry_count": 0,
        "pdf_path": "unused.pdf",
        "module_name": "login",
        "pages": [],
        "requirements": "",
        "test_cases": [],
    }))

    result = workflow.invoke(initial_state)

    # The invalid case should trigger exactly one correction.
    assert correction_calls["count"] == 1
    assert result["retry_count"] == 1

    # The corrected case should pass validation.
    assert result["validation_errors"] == []
    assert len(result["test_cases"]) == 1
    assert result["test_cases"][0]["title"] == "Successful login"
