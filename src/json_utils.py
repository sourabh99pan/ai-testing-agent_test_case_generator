import json


def parse_llm_json(content: str) -> dict:
    content = content.strip()

    # Remove Markdown code fences, if present
    if content.startswith("```"):
        lines = content.splitlines()
        lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    return json.loads(content)