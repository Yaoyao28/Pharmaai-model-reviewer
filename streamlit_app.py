from __future__ import annotations

from pathlib import Path
from typing import Any

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


# =========================================================
# Project root
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent


# =========================================================
# Comparison configurations
# =========================================================

COMPARISON_CONFIGS: dict[str, dict[str, Any]] = {
    "Compartment Model": {
        "reference_model": "ONE_COMP",
        "candidate_model": "TWO_COMP",

        "reference_estimates_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_1"
            / "estimates_1comp.xlsx"
        ),

        "reference_metrics_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_1"
            / "metrics_1comp.xlsx"
        ),

        "reference_gof_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_1"
            / "gof_1comp.png"
        ),

        "candidate_estimates_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_2"
            / "estimates_2comp.xlsx"
        ),

        "candidate_metrics_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_2"
            / "metrics_2comp.xlsx"
        ),

        "candidate_gof_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "compartment"
            / "model_2"
            / "gof_2comp.png"
        ),

        "reference_sheet": "ONE_COMP",
        "candidate_sheet": "TWO_COMP",

        "description": (
            "Compare one-compartment and two-compartment "
            "structural models."
        ),
    },

    "Absorption Model": {
        "reference_model": "ZERO_ORDER",
        "candidate_model": "FIRST_ORDER",

        "reference_estimates_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_1"
            / "estimates_zero_order.xlsx"
        ),

        "reference_metrics_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_1"
            / "metrics_zero_order.xlsx"
        ),

        "reference_gof_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_1"
            / "gof_zero_order.png"
        ),

        "candidate_estimates_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_2"
            / "estimates_first_order.xlsx"
        ),

        "candidate_metrics_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_2"
            / "metrics_first_order.xlsx"
        ),

        "candidate_gof_path": (
            PROJECT_ROOT
            / "data"
            / "demo"
            / "absorption"
            / "model_2"
            / "gof_first_order.png"
        ),

        "reference_sheet": "ZERO_ORDER",
        "candidate_sheet": "FIRST_ORDER",

        "description": (
            "Compare zero-order and first-order absorption "
            "within the same one-compartment structure."
        ),
    },
}


# =========================================================
# Metrics used in the difference table
# =========================================================

SELECTED_METRICS = [
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


# =========================================================
# Streamlit page setup
# =========================================================

st.set_page_config(
    page_title="PharmaAI Model Review",
    page_icon="📊",
    layout="wide",
)

st.title("Candidate Model Comparison")

st.write(
    "Compare model metrics, parameter estimates, and "
    "diagnostic plots for candidate pharmacometric models."
)


# =========================================================
# Select comparison type
# =========================================================

comparison_type = st.selectbox(
    "Comparison Type",
    options=list(COMPARISON_CONFIGS.keys()),
)

config = COMPARISON_CONFIGS[comparison_type]

reference_model = config["reference_model"]
candidate_model = config["candidate_model"]

st.info(
    f"Current comparison: "
    f"{reference_model} vs {candidate_model}"
)

st.caption(config["description"])


# =========================================================
# Run comparison
# =========================================================

if st.button(
    "Run Model Comparison",
    type="primary",
):
    try:
        required_paths = [
            config["reference_estimates_path"],
            config["reference_metrics_path"],
            config["candidate_estimates_path"],
            config["candidate_metrics_path"],
            config["reference_gof_path"],
            config["candidate_gof_path"],
        ]

        missing_paths = [
            path
            for path in required_paths
            if not path.exists()
        ]

        if missing_paths:
            missing_text = "\n".join(
                str(path)
                for path in missing_paths
            )

            raise FileNotFoundError(
                "The following required files are missing:\n"
                f"{missing_text}"
            )

        reference_estimates = pd.read_excel(
            config["reference_estimates_path"],
            sheet_name=config["reference_sheet"],
        )

        reference_metrics = pd.read_excel(
            config["reference_metrics_path"],
            sheet_name=config["reference_sheet"],
        )

        candidate_estimates = pd.read_excel(
            config["candidate_estimates_path"],
            sheet_name=config["candidate_sheet"],
        )

        candidate_metrics = pd.read_excel(
            config["candidate_metrics_path"],
            sheet_name=config["candidate_sheet"],
        )

        validate_estimate_table(
            reference_estimates,
            reference_model,
        )

        validate_estimate_table(
            candidate_estimates,
            candidate_model,
        )

        validate_metric_table(
            reference_metrics,
            reference_model,
        )

        validate_metric_table(
            candidate_metrics,
            candidate_model,
        )

        estimate_comparison = compare_estimates(
            {
                reference_model: reference_estimates,
                candidate_model: candidate_estimates,
            }
        )

        metric_comparison = compare_metrics(
            {
                reference_model: reference_metrics,
                candidate_model: candidate_metrics,
            }
        )

        available_metrics = set(
            metric_comparison["Metric"].tolist()
        )

        selected_metrics = [
            metric
            for metric in SELECTED_METRICS
            if metric in available_metrics
        ]

        metric_differences = calculate_metric_differences(
            metric_comparison=metric_comparison,
            reference_model=reference_model,
            candidate_model=candidate_model,
            selected_metrics=selected_metrics,
        )

        st.session_state["comparison_results"] = {
            "comparison_type": comparison_type,
            "reference_model": reference_model,
            "candidate_model": candidate_model,
            "metric_comparison": metric_comparison,
            "metric_differences": metric_differences,
            "estimate_comparison": estimate_comparison,
            "reference_gof_path": config["reference_gof_path"],
            "candidate_gof_path": config["candidate_gof_path"],
        }

        st.success(
            "Model comparison completed successfully."
        )

    except FileNotFoundError as error:
        st.error(
            "One or more required files could not be found."
        )

        st.code(str(error))

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(
            "An unexpected error occurred."
        )

        st.exception(error)


# =========================================================
# Display results
# =========================================================

results = st.session_state.get("comparison_results")

if results is not None:
    if results["comparison_type"] != comparison_type:
        st.warning(
            "The displayed results belong to another "
            "comparison type. Click Run Model Comparison "
            "to refresh the results."
        )

    else:
        result_reference = results["reference_model"]
        result_candidate = results["candidate_model"]

        st.divider()

        # -------------------------------------------------
        # Model metrics
        # -------------------------------------------------

        st.subheader("Model Metrics")

        st.caption(
            "Side-by-side comparison of model fit, "
            "estimation, shrinkage, and dataset metrics."
        )

        st.dataframe(
            results["metric_comparison"],
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------
        # Metric differences
        # -------------------------------------------------

        st.subheader("Selected Metric Differences")

        st.caption(
            f"Difference = "
            f"{result_candidate} - {result_reference}"
        )

        st.dataframe(
            results["metric_differences"],
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------
        # Parameter estimates
        # -------------------------------------------------

        st.subheader("Parameter Estimate Comparison")

        st.caption(
            "An outer merge is used, so parameters present "
            "in only one model are retained."
        )

        st.dataframe(
            results["estimate_comparison"],
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------
        # Diagnostic plots
        # -------------------------------------------------

        st.subheader("Diagnostic Plot Comparison")

        st.caption(
            "Compare goodness-of-fit plots using the same "
            "plot types and axis conventions for both models."
        )

        plot_column_1, plot_column_2 = st.columns(2)

        with plot_column_1:
            st.markdown(
                f"#### {result_reference}"
            )

            st.image(
                str(results["reference_gof_path"]),
                caption=(
                    f"{result_reference} diagnostic plots"
                ),
                use_container_width=True,
            )

        with plot_column_2:
            st.markdown(
                f"#### {result_candidate}"
            )

            st.image(
                str(results["candidate_gof_path"]),
                caption=(
                    f"{result_candidate} diagnostic plots"
                ),
                use_container_width=True,
            )

        # -------------------------------------------------
        # Reviewer interpretation
        # -------------------------------------------------

        st.divider()

        st.subheader("Reviewer Interpretation")

        selected_model = st.radio(
            "Preferred Model",
            options=[
                result_reference,
                result_candidate,
            ],
            horizontal=True,
        )

        reviewer_comment = st.text_area(
            "Reviewer Comment",
            placeholder=(
                "Consider OFV, AIC, BIC, convergence, "
                "parameter estimates, residual patterns, "
                "diagnostic plots, and scientific plausibility."
            ),
            height=140,
        )

        st.write(
            f"Selected model: **{selected_model}**"
        )

        if reviewer_comment.strip():
            st.write("Reviewer comment:")
            st.write(reviewer_comment)