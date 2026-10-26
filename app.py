
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from agents.langgraph_test_case_workflow import build_workflow


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Testing Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 18px 20px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    .hero {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(
            120deg, #173b72 0%, #2563a6 100%
        );
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero p {
        color: #e5efff;
        margin-bottom: 0;
    }

    .section-heading {
        font-size: 1.2rem;
        font-weight: 650;
        margin: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def json_download(data, filename):
    return st.download_button(
        label="⬇️ Download JSON",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )


def clear_previous_results():
    st.session_state.pop("result", None)
    st.session_state.pop("module_name", None)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🤖 AI Testing Agent")
    st.caption("AI-powered QA workspace")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Requirements",
            "Test Cases",
            "Coverage Report",
        ],
        key="navigation",
    )

    st.divider()
    st.markdown("### ⚙️ Test Configuration")

    module_name = st.selectbox(
        "Application module",
        ["login", "pim", "leave"],
        format_func=lambda value: value.upper(),
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF manual",
        type=["pdf"],
        help="Upload the user manual to analyze.",
    )

    generate_clicked = st.button(
        "🚀 Generate Test Cases",
        type="primary",
        use_container_width=True,
        disabled=uploaded_pdf is None,
    )

    st.divider()
    st.caption("Built with Python, Streamlit and LangGraph")


# --------------------------------------------------
# Application header
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>AI Testing Agent</h1>
        <p>
            Transform software manuals into structured test cases
            with AI-powered requirement analysis and coverage reporting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Run workflow
# --------------------------------------------------
if generate_clicked:
    clear_previous_results()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / Path(uploaded_pdf.name).name
            pdf_path.write_bytes(uploaded_pdf.getvalue())

            initial_state = {
                "pdf_path": str(pdf_path),
                "module_name": module_name,
                "pages": [],
                "requirements": "",
                "requirements_list": [],
                "test_cases": [],
                "validation_errors": [],
                "coverage_gaps": [],
                "coverage_report": {},
                "retry_count": 0,
            }

            progress = st.progress(0, text="Starting workflow...")

            progress.progress(
                20, text="Extracting PDF content and requirements..."
            )

            workflow = build_workflow()
            result = workflow.invoke(initial_state)

            progress.progress(
                100, text="Workflow completed successfully!"
            )

        st.session_state["result"] = result
        st.session_state["module_name"] = module_name
        st.session_state["source_filename"] = uploaded_pdf.name

        st.success("Test generation completed!")

    except Exception as exc:
        st.error(f"Workflow failed: {exc}")
        st.info(
            "Check the PowerShell terminal for the full traceback "
            "if more debugging details are needed."
        )


# --------------------------------------------------
# Load results from session
# --------------------------------------------------
result = st.session_state.get("result")
result_module = st.session_state.get("module_name", "")
source_filename = st.session_state.get("source_filename", "")

if result:
    test_cases = result.get("test_cases", [])
    requirements = result.get("requirements_list", [])
    coverage = result.get("coverage_report", {})
    errors = result.get("validation_errors", [])
else:
    test_cases = []
    requirements = []
    coverage = {}
    errors = []


# --------------------------------------------------
# Dashboard
# --------------------------------------------------
if page == "Dashboard":
    st.subheader("Dashboard")
    st.caption("Your test generation workspace at a glance.")

    if result:
        total_requirements = len(requirements)
        total_cases = len(test_cases)
        coverage_pct = coverage.get("coverage_percentage", 0)
        uncovered = coverage.get(
            "uncovered_requirements",
            len(result.get("coverage_gaps", [])),
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Requirements", total_requirements)
        col2.metric("Test Cases", total_cases)
        col3.metric("Est. Coverage", f"{coverage_pct}%")
        col4.metric("Validation Errors", len(errors))

        st.divider()

        left, right = st.columns([1.3, 1])

        with left:
            st.markdown("#### Latest run")
            st.write(f"**Module:** {result_module.upper()}")
            st.write(f"**Source PDF:** {source_filename}")
            st.write("**Workflow status:** Completed")

            st.markdown("#### Test generation summary")
            st.write(
                f"Generated **{total_cases}** test cases from "
                f"**{total_requirements}** extracted requirements."
            )

        with right:
            st.markdown("#### Requirement coverage")
            st.progress(
                max(0.0, min(float(coverage_pct) / 100, 1.0)),
                text=f"{coverage_pct}% estimated coverage",
            )
            st.write(f"Potentially uncovered: **{uncovered}**")

            if errors:
                st.warning("Some structural validation errors remain.")
            else:
                st.success("No structural validation errors reported.")

        st.divider()
        st.markdown("#### Recent generated test cases")

        if test_cases:
            preview = [
                {
                    "Test Case ID": case.get("test_case_id", ""),
                    "Title": case.get("title", ""),
                    "Priority": case.get("priority", ""),
                }
                for case in test_cases[:5]
            ]

            st.dataframe(
                pd.DataFrame(preview),
                use_container_width=True,
                hide_index=True,
            )

        st.info(
            "Use the sidebar to explore requirements, test cases, "
            "and the coverage report."
        )

    else:
        st.info(
            "Upload a PDF manual and click **Generate Test Cases** "
            "in the sidebar to begin."
        )

        st.markdown("#### Workflow")
        step1, step2, step3 = st.columns(3)

        step1.markdown("### 1. 📄")
        step1.markdown("**Extract requirements**")
        step1.caption("Read the PDF manual and identify requirements.")

        step2.markdown("### 2. 🧪")
        step2.markdown("**Generate test cases**")
        step2.caption("Create structured cases and validate their format.")

        step3.markdown("### 3. 📊")
        step3.markdown("**Analyze coverage**")
        step3.caption("Review estimated coverage and potential gaps.")


# --------------------------------------------------
# Requirements page
# --------------------------------------------------
elif page == "Requirements":
    st.subheader("📋 Extracted Requirements")

    if not result:
        st.info("Generate test cases first to view requirements.")
    else:
        st.caption(f"Module: {result_module.upper()}")
        st.metric("Total requirements", len(requirements))

        if requirements:
            for index, requirement in enumerate(requirements, start=1):
                with st.container(border=True):
                    st.markdown(f"**Requirement {index}**")
                    st.write(requirement)

            json_download(
                {
                    "module": result_module,
                    "requirements": requirements,
                },
                f"{result_module}_requirements.json",
            )
        else:
            st.warning("No requirements were extracted.")


# --------------------------------------------------
# Test cases page
# --------------------------------------------------
elif page == "Test Cases":
    st.subheader("🧪 Generated Test Cases")

    if not result:
        st.info("Generate test cases first to view the results.")
    elif not test_cases:
        st.warning("The workflow did not generate any test cases.")
    else:
        st.caption(f"Module: {result_module.upper()}")

        search_text = st.text_input(
            "Search test cases",
            placeholder="Search by ID or title...",
        )

        priority_options = sorted(
            {
                str(case.get("priority", "Unknown"))
                for case in test_cases
            }
        )

        selected_priorities = st.multiselect(
            "Filter by priority",
            options=priority_options,
            default=priority_options,
        )

        filtered_cases = [
            case for case in test_cases
            if selected_priorities
            and str(case.get("priority", "Unknown")) in selected_priorities
            and (
                search_text.strip().lower() in
                (
                    str(case.get("test_case_id", ""))
                    + " "
                    + str(case.get("title", ""))
                ).lower()
            )
        ]

        table_data = [
            {
                "ID": case.get("test_case_id", ""),
                "Title": case.get("title", ""),
                "Priority": case.get("priority", ""),
                "Steps": len(case.get("steps", [])),
            }
            for case in filtered_cases
        ]

        st.dataframe(
            pd.DataFrame(table_data),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Showing {len(filtered_cases)} of {len(test_cases)} test cases."
        )

        if filtered_cases:
            selected_id = st.selectbox(
                "Select a test case to inspect",
                options=[
                    case.get("test_case_id")
                    for case in filtered_cases
                ],
            )

            selected_case = next(
                case for case in filtered_cases
                if case.get("test_case_id") == selected_id
            )

            st.divider()
            st.markdown(f"### {selected_case.get('title', 'Test case')}")

            st.write(
                f"**ID:** {selected_case.get('test_case_id', '')}"
            )
            st.write(
                f"**Priority:** {selected_case.get('priority', '')}"
            )

            st.markdown("#### Preconditions")
            preconditions = selected_case.get("preconditions", [])
            if isinstance(preconditions, list):
                for item in preconditions:
                    st.markdown(f"- {item}")
            else:
                st.write(preconditions)

            st.markdown("#### Steps")
            steps = selected_case.get("steps", [])
            if isinstance(steps, list):
                for index, step in enumerate(steps, start=1):
                    st.markdown(f"{index}. {step}")
            else:
                st.write(steps)

            st.markdown("#### Expected result")
            st.write(selected_case.get("expected_result", "Not specified"))

            st.markdown("#### Assumptions")
            assumptions = selected_case.get("assumptions", [])
            if isinstance(assumptions, list) and assumptions:
                for assumption in assumptions:
                    st.markdown(f"- {assumption}")
            elif assumptions:
                st.write(assumptions)
            else:
                st.caption("No assumptions recorded.")

        st.divider()

        json_download(
            test_cases,
            f"{result_module}_test_cases.json",
        )


# --------------------------------------------------
# Coverage report page
# --------------------------------------------------
elif page == "Coverage Report":
    st.subheader("📊 Requirement Coverage Report")

    if not result:
        st.info("Generate test cases first to view coverage.")
    elif not coverage:
        st.warning("No coverage report was returned by the workflow.")
    else:
        coverage_pct = coverage.get("coverage_percentage", 0)
        total = coverage.get("total_requirements", len(requirements))
        covered = coverage.get("covered_requirements", 0)
        uncovered = coverage.get("uncovered_requirements", 0)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Requirements", total)
        col2.metric("Covered Requirements", covered)
        col3.metric("Uncovered Requirements", uncovered)

        st.markdown("#### Estimated coverage")
        st.progress(
            max(0.0, min(float(coverage_pct) / 100, 1.0)),
            text=f"{coverage_pct}% estimated coverage",
        )

        st.caption(
            "Coverage is an LLM-assisted estimate, not proof that "
            "the test cases fully verify the requirements."
        )

        coverage_results = coverage.get("results", [])

        if coverage_results:
            st.markdown("#### Requirement-to-test-case mapping")

            coverage_table = [
                {
                    "Requirement": item.get("requirement", ""),
                    "Covered": (
                        "Covered" if item.get("covered") else "Uncovered"
                    ),
                    "Matching Test Case IDs": ", ".join(
                        item.get("matching_test_case_ids", [])
                    ),
                }
                for item in coverage_results
            ]

            st.dataframe(
                pd.DataFrame(coverage_table),
                use_container_width=True,
                hide_index=True,
            )

            for index, item in enumerate(coverage_results, start=1):
                with st.expander(f"Requirement {index} details"):
                    st.write(item.get("requirement", ""))
                    st.write(
                        "**Status:** "
                        + (
                            "Covered"
                            if item.get("covered")
                            else "Uncovered"
                        )
                    )
                    st.write(
                        "**Matching test cases:** "
                        + ", ".join(
                            item.get("matching_test_case_ids", [])
                        )
                    )
                    st.write(
                        "**Explanation:** "
                        + item.get("explanation", "No explanation provided.")
                    )

        gaps = coverage.get(
            "coverage_gaps",
            result.get("coverage_gaps", []),
        )

        st.markdown("#### Potential coverage gaps")

        if gaps:
            for gap in gaps:
                st.warning(gap)
        else:
            st.success("No uncovered requirements were reported.")

        st.divider()

        json_download(
            coverage,
            f"{result_module}_coverage.json",
        )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "AI Testing Agent • Python • Streamlit • LangGraph • LLM-assisted QA"
)
