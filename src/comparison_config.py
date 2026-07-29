from __future__ import annotations

from typing import Any


COMPARISON_CONFIGS: dict[str, dict[str, Any]] = {
    "Compartment Model": {
        "reference_model": "ONE_COMP",
        "candidate_model": "TWO_COMP",
        "reference_estimates_path": (
            "data/demo/compartment/model_1/estimates_1comp.xlsx"
        ),
        "reference_metrics_path": (
            "data/demo/compartment/model_1/metrics_1comp.xlsx"
        ),
        "candidate_estimates_path": (
            "data/demo/compartment/model_2/estimates_2comp.xlsx"
        ),
        "candidate_metrics_path": (
            "data/demo/compartment/model_2/metrics_2comp.xlsx"
        ),
        "reference_sheet": "ONE_COMP",
        "candidate_sheet": "TWO_COMP",
    },
    "Absorption Model": {
        "reference_model": "ZERO_ORDER",
        "candidate_model": "FIRST_ORDER",
        "reference_estimates_path": (
            "data/demo/absorption/model_1/estimates_zero_order.xlsx"
        ),
        "reference_metrics_path": (
            "data/demo/absorption/model_1/metrics_zero_order.xlsx"
        ),
        "candidate_estimates_path": (
            "data/demo/absorption/model_2/estimates_first_order.xlsx"
        ),
        "candidate_metrics_path": (
            "data/demo/absorption/model_2/metrics_first_order.xlsx"
        ),
        "reference_sheet": "ZERO_ORDER",
        "candidate_sheet": "FIRST_ORDER",
    },
}


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