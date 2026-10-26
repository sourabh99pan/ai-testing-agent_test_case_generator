
from agents.test_case_generator import generate_test_cases


def test_generate_test_cases():
    requirements = """
    The user enters a username and password to log in.
    The user can change their password using the Change Password link.
    """

    test_cases = generate_test_cases(requirements)

    assert len(test_cases) > 0
    assert "test_case_id" in test_cases[0]
    assert "expected_result" in test_cases[0]

    print(test_cases)
