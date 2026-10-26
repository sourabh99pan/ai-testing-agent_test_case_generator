
import agents.langgraph_test_case_workflow as workflow_module


def test_langgraph_stops_after_max_retries(monkeypatch):
    correction_calls = {"count": 0}

    def fake_extract_document(state):
        return {
            "pages": [],
            "requirements": "Login requirement",
        }

    def fake_generate_cases(state):
        return {
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "Incomplete test case",
                }
            ]
        }

    def fake_correct_cases(state):
        correction_calls["count"] += 1

        # Keep returning invalid data to force repeated retries.
        return {
            "test_cases": [
                {
                    "test_case_id": "TC001",
                    "title": "Still incomplete",
                }
            ],
            "retry_count": state["retry_count"] + 1,
        }

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

    result = workflow.invoke(initial_state)

    assert correction_calls["count"] == workflow_module.MAX_RETRIES
    assert result["retry_count"] == workflow_module.MAX_RETRIES
    assert result["validation_errors"]
