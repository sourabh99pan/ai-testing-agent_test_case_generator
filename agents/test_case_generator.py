
import json

from src.json_utils import parse_llm_json
from src.llm_client import get_llm


def generate_test_cases(requirements: str) -> list[dict]:
    llm = get_llm()

    prompt = f"""
You are an experienced QA engineer.

Generate test cases based ONLY on the requirements below.

Rules:
- Include positive and negative test cases where supported.
- Do not invent application behavior or error messages.
- If a detail is unspecified, mention it as an assumption
  or clarification needed.
- Return valid JSON only, with no Markdown fences.

Use this JSON structure:
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

Requirements:
{requirements}
"""

    response = llm.invoke(prompt)
    print("LLM RAW RESPONSE:", repr(response.content))
    #result = json.loads(response.content)
    result = parse_llm_json(response.content)
    return result["test_cases"]
