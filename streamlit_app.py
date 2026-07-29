from __future__ import annotations

import pandas as pd
import streamlit as st

from src.comparison import (
    calculate_metric_differences,
    compare_estimates,
    compare_metrics,
)
from src.validation import (
    validate_estimate_table,
    validate_metric_table,
)


REFERENCE_MODEL = "ONE_COMP"
CANDIDATE_MODEL = "TWO_COMP"


st.set_page_config(
    page_title="PharmaAI Model Review",
    layout="wide",
)

st.title("Candidate Model Comparison")

st.write(
    "Compare pharmacometric model metrics and parameter "
    "estimates using Pumas model results."
)

comparison_type = st.selectbox(
    "Comparison Type",
    [
        "Compartment Model",
        "Absorption Model",
        "Residual Error Model",
        "Covariate Model",
    ],
)

st.info(
    f"Current comparison: "
    f"{REFERENCE_MODEL} vs {CANDIDATE_MODEL}"
)


if st.button(
    "Run Model Comparison",
    type="primary",
):
    try:
        estimates_1 = pd.read_excel(
            "data/demo/model_1/estimates_1comp.xlsx",
            sheet_name="ONE_COMP",
        )

        metrics_1 = pd.read_excel(
            "data/demo/model_1/metrics_1comp.xlsx",
            sheet_name="ONE_COMP",
        )

        estimates_2 = pd.read_excel(
            "data/demo/model_2/estimates_2comp.xlsx",
            sheet_name="TWO_COMP",
        )

        metrics_2 = pd.read_excel(
            "data/demo/model_2/metrics_2comp.xlsx",
            sheet_name="TWO_COMP",
        )

        validate_estimate_table(
            estimates_1,
            REFERENCE_MODEL,
        )

        validate_estimate_table(
            estimates_2,
            CANDIDATE_MODEL,
        )

        validate_metric_table(
            metrics_1,
            REFERENCE_MODEL,
        )

        validate_metric_table(
            metrics_2,
            CANDIDATE_MODEL,
        )

        estimate_comparison = compare_estimates(
            {
                REFERENCE_MODEL: estimates_1,
                CANDIDATE_MODEL: estimates_2,
            }
        )

        metric_comparison = compare_metrics(
            {
                REFERENCE_MODEL: metrics_1,
                CANDIDATE_MODEL: metrics_2,
            }
        )

        selected_metrics = [
            "-2LL",
            "AIC",
            "BIC",
            "Estimation Time",
            "Optimized Parameters",
            "(η-shrinkage) η₁",
            "(η-shrinkage) η₂",
            "(η-shrinkage) η₃",
            "(η-shrinkage) η₄",
            "(η-shrinkage) η₅",
            "(ε-shrinkage) conc",
        ]

        metric_differences = (
            calculate_metric_differences(
                metric_comparison=metric_comparison,
                reference_model=REFERENCE_MODEL,
                candidate_model=CANDIDATE_MODEL,
                selected_metrics=selected_metrics,
            )
        )

        st.session_state["comparison_ready"] = True

        st.session_state["metric_comparison"] = (
            metric_comparison
        )

        st.session_state["metric_differences"] = (
            metric_differences
        )

        st.session_state["estimate_comparison"] = (
            estimate_comparison
        )

        st.success(
            "Model comparison completed successfully."
        )

    except FileNotFoundError as error:
        st.error(
            "One or more Excel files could not be found."
        )
        st.exception(error)

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "An unexpected error occurred."
        )
        st.exception(error)


if st.session_state.get("comparison_ready"):
    st.header("Model Metrics")

    st.dataframe(
        st.session_state["metric_comparison"],
        use_container_width=True,
        hide_index=True,
    )

    st.header("Selected Metric Differences")

    st.caption(
        f"Difference = {CANDIDATE_MODEL} - "
        f"{REFERENCE_MODEL}"
    )

    st.dataframe(
        st.session_state["metric_differences"],
        use_container_width=True,
        hide_index=True,
    )

    st.header("Parameter Estimate Comparison")

    st.dataframe(
        st.session_state["estimate_comparison"],
        use_container_width=True,
        hide_index=True,
    )

    st.header("Reviewer Interpretation")

    selected_model = st.radio(
        "Preferred Model",
        [
            REFERENCE_MODEL,
            CANDIDATE_MODEL,
        ],
    )

    reviewer_comment = st.text_area(
        "Reviewer Comment",
        placeholder=(
            "Example: TWO_COMP had lower AIC and BIC, "
            "while both models converged successfully."
        ),
    )

    st.write(
        f"Selected model: **{selected_model}**"
    )

    if reviewer_comment:
        st.write("Reviewer comment:")
        st.write(reviewer_comment)