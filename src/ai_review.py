from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


MODEL_SELECTION_METRICS = (
    "OFV",
    "-2LL",
    "AIC",
    "BIC",
)

SUCCESS_METRIC_NAMES = (
    "Successful",
    "Converged",
    "Successful Minimization",
)

COVARIANCE_METRIC_NAMES = (
    "Covariance Step",
    "Covariance",
    "Covariance Successful",
)


def _normalize_text(value: object) -> str:
    return str(value).strip().lower()


def _find_metric_row(
    metric_comparison: pd.DataFrame,
    possible_names: Sequence[str],
) -> pd.Series | None:
    """Find the first matching metric row, case-insensitively."""

    if "Metric" not in metric_comparison.columns:
        raise ValueError(
            "Metric comparison must contain a 'Metric' column."
        )

    normalized_metrics = (
        metric_comparison["Metric"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    for possible_name in possible_names:
        matches = metric_comparison[
            normalized_metrics == _normalize_text(possible_name)
        ]

        if not matches.empty:
            return matches.iloc[0]

    return None


def _get_metric_value(
    metric_comparison: pd.DataFrame,
    model_name: str,
    possible_names: Sequence[str],
) -> object | None:
    """Return one raw metric value for one model."""

    if model_name not in metric_comparison.columns:
        raise ValueError(
            f"Metric comparison does not contain "
            f"model column '{model_name}'."
        )

    row = _find_metric_row(
        metric_comparison,
        possible_names,
    )

    if row is None:
        return None

    value = row[model_name]

    if pd.isna(value):
        return None

    return value


def _get_numeric_metric(
    metric_comparison: pd.DataFrame,
    model_name: str,
    metric_name: str,
) -> float | None:
    """Return a numeric metric or None when unavailable."""

    value = _get_metric_value(
        metric_comparison,
        model_name,
        (metric_name,),
    )

    if value is None:
        return None

    numeric_value = pd.to_numeric(
        pd.Series([value]),
        errors="coerce",
    ).iloc[0]

    if pd.isna(numeric_value):
        return None

    return float(numeric_value)


def _normalize_status(value: object | None) -> str:
    """Convert common status values to passed, failed, or unknown."""

    if value is None:
        return "unknown"

    normalized = _normalize_text(value)

    if normalized in {
        "true",
        "yes",
        "pass",
        "passed",
        "success",
        "successful",
        "1",
    }:
        return "passed"

    if normalized in {
        "false",
        "no",
        "fail",
        "failed",
        "failure",
        "0",
    }:
        return "failed"

    return "unknown"


def _get_model_parameters(
    parameter_comparison: pd.DataFrame,
    model_name: str,
) -> list[str]:
    """
    Return parameters with an estimate for one model.

    Expected estimate column:
        '<MODEL NAME> Estimate'
    """

    if "parameter" not in parameter_comparison.columns:
        raise ValueError(
            "Parameter comparison must contain "
            "a 'parameter' column."
        )

    estimate_column = f"{model_name} Estimate"

    if estimate_column not in parameter_comparison.columns:
        raise ValueError(
            f"Parameter comparison does not contain "
            f"'{estimate_column}'."
        )

    return (
        parameter_comparison.loc[
            parameter_comparison[estimate_column].notna(),
            "parameter",
        ]
        .astype(str)
        .str.strip()
        .tolist()
    )


def _build_metric_evidence(
    metric_comparison: pd.DataFrame,
    reference_model: str,
    candidate_model: str,
) -> dict[str, dict[str, float | None]]:
    """
    Build deterministic fit-metric evidence.

    Difference direction:
        candidate minus reference
    """

    evidence: dict[
        str,
        dict[str, float | None],
    ] = {}

    for metric_name in MODEL_SELECTION_METRICS:
        reference_value = _get_numeric_metric(
            metric_comparison,
            reference_model,
            metric_name,
        )
        candidate_value = _get_numeric_metric(
            metric_comparison,
            candidate_model,
            metric_name,
        )

        difference = None

        if (
            reference_value is not None
            and candidate_value is not None
        ):
            difference = candidate_value - reference_value

        evidence[metric_name] = {
            "reference_value": reference_value,
            "candidate_value": candidate_value,
            "candidate_minus_reference": difference,
        }

    return evidence


def build_two_model_evidence(
    stage_name: str,
    reference_model: str,
    candidate_model: str,
    metric_comparison: pd.DataFrame,
    parameter_comparison: pd.DataFrame,
    reference_gof_available: bool,
    candidate_gof_available: bool,
) -> dict[str, Any]:
    """
    Build provider-independent evidence for any two-model comparison.

    No model names are hard-coded. This can support absorption,
    disposition, elimination, and other user-defined comparisons.
    """

    reference_parameters = set(
        _get_model_parameters(
            parameter_comparison,
            reference_model,
        )
    )
    candidate_parameters = set(
        _get_model_parameters(
            parameter_comparison,
            candidate_model,
        )
    )

    return {
        "review_type": "two_model_comparison",
        "stage": stage_name,
        "reference_model": reference_model,
        "candidate_model": candidate_model,
        "difference_definition": "Candidate minus reference.",
        "fit_metrics": _build_metric_evidence(
            metric_comparison,
            reference_model,
            candidate_model,
        ),
        "estimation_status": {
            reference_model: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    reference_model,
                    SUCCESS_METRIC_NAMES,
                )
            ),
            candidate_model: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    candidate_model,
                    SUCCESS_METRIC_NAMES,
                )
            ),
        },
        "covariance_status": {
            reference_model: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    reference_model,
                    COVARIANCE_METRIC_NAMES,
                )
            ),
            candidate_model: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    candidate_model,
                    COVARIANCE_METRIC_NAMES,
                )
            ),
        },
        "parameters": {
            "shared": sorted(
                reference_parameters & candidate_parameters
            ),
            "unique_to_reference": sorted(
                reference_parameters - candidate_parameters
            ),
            "unique_to_candidate": sorted(
                candidate_parameters - reference_parameters
            ),
        },
        "gof_images": {
            reference_model: reference_gof_available,
            candidate_model: candidate_gof_available,
        },
        "limitations": [
            (
                "The LLM receives only GOF image availability and "
                "does not visually interpret the plots."
            ),
            (
                "Parameter plausibility and precision require "
                "human pharmacometric review."
            ),
            (
                "The candidates should use the same dataset and "
                "comparable estimation settings."
            ),
        ],
    }


def build_residual_error_evidence(
    model_names: Sequence[str],
    reference_model: str,
    metric_comparison: pd.DataFrame,
    parameter_comparison: pd.DataFrame,
    gof_availability: Mapping[str, bool],
) -> dict[str, Any]:
    """Build provider-independent evidence for residual-error review."""

    if reference_model not in model_names:
        raise ValueError(
            f"Reference model '{reference_model}' is not "
            "included in model_names."
        )

    pairwise_fit_metrics = {}

    for candidate_model in model_names:
        if candidate_model == reference_model:
            continue

        comparison_name = (
            f"{candidate_model} minus {reference_model}"
        )
        pairwise_fit_metrics[comparison_name] = (
            _build_metric_evidence(
                metric_comparison,
                reference_model,
                candidate_model,
            )
        )

    return {
        "review_type": "residual_error_model_comparison",
        "stage": "Residual Error Model Selection",
        "models_compared": list(model_names),
        "reference_model": reference_model,
        "difference_definition": "Candidate minus reference.",
        "pairwise_fit_metrics": pairwise_fit_metrics,
        "estimation_status": {
            model_name: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    model_name,
                    SUCCESS_METRIC_NAMES,
                )
            )
            for model_name in model_names
        },
        "covariance_status": {
            model_name: _normalize_status(
                _get_metric_value(
                    metric_comparison,
                    model_name,
                    COVARIANCE_METRIC_NAMES,
                )
            )
            for model_name in model_names
        },
        "parameters_by_model": {
            model_name: _get_model_parameters(
                parameter_comparison,
                model_name,
            )
            for model_name in model_names
        },
        "gof_images": {
            model_name: bool(
                gof_availability.get(model_name, False)
            )
            for model_name in model_names
        },
        "limitations": [
            (
                "The LLM receives only GOF image availability and "
                "does not visually interpret the plots."
            ),
            (
                "The final residual-error selection requires "
                "human pharmacometric confirmation."
            ),
            (
                "Additional complexity should be justified by "
                "estimability and diagnostic improvement."
            ),
        ],
    }


def build_final_model_evidence(
    absorption_model: str,
    structural_model: str,
    residual_error_model: str,
    reviewer_decision: str | None = None,
    reviewer_comments: str | None = None,
) -> dict[str, Any]:
    """Build provider-independent final-model evidence."""

    return {
        "review_type": "final_base_model",
        "selected_models": {
            "absorption_model": absorption_model,
            "structural_model": structural_model,
            "residual_error_model": residual_error_model,
        },
        "final_model": (
            f"{absorption_model} + "
            f"{structural_model} + "
            f"{residual_error_model}"
        ),
        "reviewer_decision": (
            reviewer_decision or "Not recorded"
        ),
        "reviewer_comments": (
            reviewer_comments
            or "No reviewer comments provided."
        ),
        "remaining_checks": [
            "Confirm successful minimization.",
            "Confirm covariance-step success.",
            "Confirm parameter precision.",
            "Confirm physiological plausibility.",
            "Confirm acceptable shrinkage.",
            "Confirm absence of systematic GOF trends.",
            (
                "Confirm that fit improvement justifies "
                "additional model complexity."
            ),
        ],
    }
