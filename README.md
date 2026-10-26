# 🤖 AI Testing Agent

**An AI-powered test case generation and requirement coverage tool built with Python, LangGraph, LLMs, and Streamlit.**

Transform software user manuals in PDF format into structured test cases. The agent extracts requirements, generates test scenarios, validates the generated output, retries corrections when necessary, and produces an LLM-assisted requirement coverage report.

## ✨ Features

- **PDF Requirement Extraction:** Extract functional requirements from software documentation using an LLM.
- **AI Test Case Generation:** Generate structured test cases with IDs, titles, preconditions, steps, expected results, priorities, and assumptions.
- **LangGraph Workflow:** Orchestrate document extraction, requirement extraction, test generation, validation, and correction retries.
- **Test Case Validation:** Check required fields, empty results, and duplicate test case IDs.
- **Requirement Coverage Analysis:** Map extracted requirements to generated test cases and identify potential coverage gaps.
- **Interactive Streamlit UI:** Upload a PDF, select a module, generate test cases, and inspect results through a browser-based interface.
- **JSON Export:** Download extracted requirements, generated test cases, and coverage reports.
- **Automated Tests:** Test core components and workflow behavior using pytest.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| LangChain | LLM integration |
| LangGraph | Workflow orchestration and retry routing |
| OpenAI API | Requirement extraction, test generation, and coverage analysis |
| Streamlit | Interactive web interface |
| PyMuPDF | PDF text extraction |
| Pydantic | Data validation support |
| pytest | Automated testing |

## 🏗️ Architecture

```text
                 PDF User Manual
                        |
                        v
                 Extract PDF Text
                        |
                        v
               Extract Requirements
                        |
                        v
                Save Requirements
                        |
                        v
                Generate Test Cases
                        |
                        v
                Validate Test Cases
                        |
                  Errors found?
                   /         \
                 Yes          No
                  |            |
                  v            |
              Correct Cases    |
                  |            |
                  +--> Validate
                               |
                               v
                   Analyze Requirement
                         Coverage
                               |
                               v
                    Save Coverage Report
                               |
                               v
                      Streamlit UI
```

The workflow uses LangGraph to manage node execution, conditional routing, and bounded correction retries.

## 📂 Project Structure

```text
ai-testing-agent/
├── agents/
│   ├── test_case_generator.py
│   └── langgraph_test_case_workflow.py
├── src/
│   ├── document_reader.py
│   ├── llm_client.py
│   └── json_utils.py
├── tests/
│   ├── test_document_reader.py
│   ├── test_llm.py
│   ├── test_case_generator.py
│   ├── test_langgraph_workflow.py
│   ├── test_langgraph_retry.py
│   ├── test_langgraph_max_retries.py
│   └── test_requirement_extraction.py
├── outputs/                 # Generated reports; not committed
├── documents/               # Local PDF manuals; not committed
├── app.py                   # Streamlit application
├── run_agent.py             # Command-line entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

*The file list above describes the intended structure; adjust filenames if your repository differs.*

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.11
- Git
- An OpenAI API key with API access and available usage quota

### 2. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-testing-agent.git
cd ai-testing-agent
```

Replace `YOUR_USERNAME` with your GitHub username.

### 3. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
```

Use a model supported by your OpenAI account and the application's LangChain integration.

**Security:** Never commit your `.env` file or expose your API key in source code, screenshots, or logs.

### 6. Provide a PDF manual

Place a PDF manual in the local `documents/` directory if you plan to use the command-line entry point. The repository does not include the original manual; use documentation you have permission to process.

The available module names and their PDF page ranges are configured in `src/document_reader.py`. Check these mappings against your PDF before running the workflow.

## 🖥️ Run the Application

### Option A: Streamlit UI

Start the web application:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually:

`http://localhost:8501`

Then:

1. Upload a PDF user manual.
2. Select the module to analyze.
3. Click **Generate Test Cases**.
4. Review extracted requirements and generated test cases.
5. Inspect the requirement coverage report.
6. Download the available JSON reports.

### Option B: Command-line workflow

Run:

```bash
python run_agent.py
```

Select one of the configured modules when prompted. The application processes the corresponding pages from the configured PDF manual.

## 📊 Output Files

The workflow saves JSON reports under `outputs/`.

| File | Description |
|---|---|
| `login_requirements.json` | Extracted requirements for the login module |
| `login_test_cases.json` | Generated login test cases |
| `login_coverage.json` | Requirement coverage analysis |
| `pim_requirements.json` | Extracted PIM requirements |
| `pim_test_cases.json` | Generated PIM test cases |
| `pim_coverage.json` | PIM coverage analysis |
| `leave_requirements.json` | Extracted Leave requirements |
| `leave_test_cases.json` | Generated Leave test cases |
| `leave_coverage.json` | Leave coverage analysis |

The actual files are generated when you run the workflow; they are not required to be present in the repository.

### Example test case structure

```json
{
  "test_case_id": "TC001",
  "title": "Successful login with valid credentials",
  "preconditions": [
    "User has valid credentials"
  ],
  "steps": [
    "Open the login page",
    "Enter a valid username",
    "Enter a valid password",
    "Click the login button"
  ],
  "expected_result": "User successfully logs in",
  "priority": "High",
  "assumptions": []
}
```

This is an illustrative example. Actual generated content depends on the source manual and LLM response.

## 🧪 Running Tests

Run the complete pytest suite:

```bash
python -m pytest -v
```

Run a specific test module:

```bash
python -m pytest tests/test_langgraph_workflow.py -v
```

Run retry-related tests:

```bash
python -m pytest tests/test_langgraph_retry.py tests/test_langgraph_max_retries.py -v
```

Some tests may call the real LLM and require a valid API key, network access, and available API quota. Mocked workflow tests can verify retry behavior without making real LLM calls.

## 📈 Understanding Coverage

The coverage report includes:

- Total extracted requirements
- Requirements marked as covered
- Requirements marked as uncovered
- Estimated coverage percentage
- Matching test case IDs
- Explanations for coverage decisions
- Potential coverage gaps

**Important:** Requirement coverage is an LLM-assisted estimate, not proof of complete or correct testing. Review the requirement-to-test-case mappings, confirm the expected behavior against the source documentation, and validate the generated tests before using them in a real QA process.

## 🔐 Security and Privacy

- Keep API keys in environment variables.
- Never commit `.env`, virtual environments, or generated artifacts.
- Avoid publishing confidential user manuals, proprietary test data, or personal information.
- Review generated test cases for unsupported assumptions before use.

## 🔮 Future Improvements

Potential enhancements include:

- Excel export for generated test cases
- Persistent run history
- Improved requirement traceability and coverage validation
- Human review and approval of generated test cases
- Automated UI test script generation using Playwright
- Deployment of the Streamlit application
- CI/CD integration and expanded automated testing

## 👨‍💻 Author

**Sourabh Pandya**

AI Testing Agent — a portfolio project exploring LLM-powered QA automation, requirement analysis, and LangGraph workflow orchestration.

If you find this project useful, consider giving the repository a ⭐ on GitHub.
