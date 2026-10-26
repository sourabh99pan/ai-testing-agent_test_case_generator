
from agents.langgraph_test_case_workflow import extract_requirements
from agents.langgraph_test_case_workflow import save_requirements


def test_extract_requirements():
    state = {
        "pdf_path": "unused.pdf",
        "module_name": "login",
        "pages": [],
        "requirements": (
            "The user enters a username and password. "
            "The user can change their password using "
            "the Change Password link."
        ),
        "requirements_list": [],
        "test_cases": [],
        "validation_errors": [],
        "coverage_gaps": [],
        "retry_count": 0,
    }

    result = extract_requirements(state)

    assert result["requirements_list"]
    assert all(
        isinstance(item, str)
        for item in result["requirements_list"]
    )

    print(result["requirements_list"])

def test_save_requirements():
    requirements = [
        "The system shall allow the user to enter a username and password.",
        "The system shall allow the user to change their password using the Change Password link.",
    ]

    save_requirements(requirements, "login")