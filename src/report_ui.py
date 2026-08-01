from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import (
    LLM_PROVIDER,
    OLLAMA_MODEL,
)
from src.pdf_report import generate_pdf_report
from src.report_builder import build_final_report


def render_final_report_section() -> None:
    """Render the final summary and PDF download button."""

    st.header("Final Model Review Report")

    selected_absorption = st.session_state.get(
        "selected_absorption_model"
    )
    selected_structural = st.session_state.get(
        "selected_structural_model"
    )
    selected_error = st.session_state.get(
        "selected_error_model"
    )

    missing: list[str] = []

    if not selected_absorption:
        missing.append("absorption model")

    if not selected_structural:
        missing.append("structural model")

    if not selected_error:
        missing.append("residual-error model")

    if missing:
        st.info(
            "Complete all three model-selection stages before "
            "generating the final PDF. Missing: "
            + ", ".join(missing)
            + "."
        )
        return

    st.success(
        "All three model components have been selected."
    )

    st.dataframe(
        pd.DataFrame(
            {
                "Component": [
                    "Absorption",
                    "Structural",
                    "Residual error",
                ],
                "Selected model": [
                    selected_absorption,
                    selected_structural,
                    selected_error,
                ],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    report_data = build_final_report(
        selected_absorption_model=selected_absorption,
        selected_structural_model=selected_structural,
        selected_error_model=selected_error,
        absorption_evidence=st.session_state.get(
            "absorption_llm_evidence"
        ),
        absorption_llm_review=st.session_state.get(
            "absorption_llm_review"
        ),
        structural_evidence=st.session_state.get(
            "structural_llm_evidence"
        ),
        structural_llm_review=st.session_state.get(
            "structural_llm_review"
        ),
        residual_error_evidence=st.session_state.get(
            "residual_llm_evidence"
        ),
        residual_error_llm_review=st.session_state.get(
            "residual_llm_review"
        ),
        llm_provider=LLM_PROVIDER,
        llm_model=OLLAMA_MODEL,
    )

    pdf_bytes = generate_pdf_report(
        report_data
    )

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=(
            "pharmaai_model_review_report.pdf"
        ),
        mime="application/pdf",
        type="primary",
    )

    with st.expander(
        "Preview structured report data"
    ):
        st.json(report_data)
