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


def _normalize_text(
    value: object,
) -> str:
    """
    Normalize text for case-insensitive matching.
    """

    return str(value).strip().lower()


def _find_metric_row(
    metric_comparison: pd.DataFrame,
    possible_names: Sequence[str],
) -> pd.Series | None:
    """
    Find the first metric row matching any supplied name.

    Matching is case-insensitive and ignores surrounding spaces.
    """

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
        normalized_target = _normalize_text(
            possible_name
        )

        matching_rows = metric_comparison[
            normalized_metrics == normalized_target
        ]

        if not matching_rows.empty:
            return matching_rows.iloc[0]

    return None


def _get_metric_value(
    metric_comparison: pd.DataFrame,
    model_name: str,
    possible_names: Sequence[str],
) -> object | None:
    """
    Return one raw metric value for one model.
    """

    if model_name not in metric_comparison.columns:
        raise ValueError(
            f"Metric comparison does not contain "
            f"model column '{model_name}'."
        )

    metric_row = _find_metric_row(
        metric_comparison=metric_comparison,
        possible_names=possible_names,
    )

    if metric_row is None:
        return None

    value = metric_row[model_name]

    if pd.isna(value):
        return None

    return value


def _get_numeric_metric(
    metric_comparison: pd.DataFrame,
    model_name: str,
    metric_name: str,
) -> float | None:
    """
    Return one numeric metric value.

    Returns None if the row is missing or cannot be converted
    to a numeric value.
    """

    value = _get_metric_value(
        metric_comparison=metric_comparison,
        model_name=model_name,
        possible_names=(
            metric_name,
        ),
    )

    if value is None:
        return None

    numeric_value = pd.to_numeric(
        pd.Series(
            [value]
        ),
        errors="coerce",
    ).iloc[0]

    if pd.isna(numeric_value):
        return None

    return float(
        numeric_value
    )


def _normalize_status(
    value: object | None,
) -> str:
    """
    Convert common model-status values into:

        passed
        failed
        unknown
    """

    if value is None:
        return "unknown"

    normalized = _normalize_text(
        value
    )

    passed_values = {
        "true",
        "yes",
        "pass",
        "passed",
        "success",
        "successful",
        "1",
    }

    failed_values = {
        "false",
        "no",
        "fail",
        "failed",
        "failure",
        "0",
    }

    if normalized in passed_values:
        return "passed"

    if normalized in failed_values:
        return "failed"

    return "unknown"


def _get_model_parameters(
    parameter_comparison: pd.DataFrame,
    model_name: str,
) -> list[str]:
    """
    Return parameters with estimates available for one model.

    Expected estimate column:

        '<MODEL NAME> Estimate'
    """

    if "parameter" not in parameter_comparison.columns:
        raise ValueError(
            "Parameter comparison must contain "
            "a 'parameter' column."
        )

    estimate_column = (
        f"{model_name} Estimate"
    )

    if estimate_column not in parameter_comparison.columns:
        raise ValueError(
            f"Parameter comparison does not contain "
            f"'{estimate_column}'."
        )

    available_parameters = (
        parameter_comparison.loc[
            parameter_comparison[
                estimate_column
            ].notna(),
            "parameter",
        ]
        .astype(str)
        .str.strip()
        .tolist()
    )

    return available_parameters


def _build_metric_evidence(
    metric_comparison: pd.DataFrame,
    reference_model: str,
    candidate_model: str,
) -> dict[str, dict[str, object]]:
    """
    Build deterministic evidence for model-selection metrics.

    For OFV, -2LL, AIC, and BIC:

        lower numeric value = numerically favored

    This rule also applies when values are negative.

    Difference direction:

        candidate minus reference
    """

    evidence: dict[
        str,
        dict[str, object],
    ] = {}

    for metric_name in MODEL_SELECTION_METRICS:
        reference_value = _get_numeric_metric(
            metric_comparison=metric_comparison,
            model_name=reference_model,
            metric_name=metric_name,
        )

        candidate_value = _get_numeric_metric(
            metric_comparison=metric_comparison,
            model_name=candidate_model,
            metric_name=metric_name,
        )

        difference: float | None = None
        favored_model: str | None = None

        interpretation = (
            "Metric unavailable for one or both models."
        )

        if (
            reference_value is not None
            and candidate_value is not None
        ):
            difference = (
                candidate_value
                - reference_value
            )

            if candidate_value < reference_value:
                favored_model = candidate_model

                interpretation = (
                    f"{candidate_model} has the lower "
                    f"{metric_name} and is numerically "
                    "favored for this metric."
                )

            elif candidate_value > reference_value:
                favored_model = reference_model

                interpretation = (
                    f"{reference_model} has the lower "
                    f"{metric_name} and is numerically "
                    "favored for this metric."
                )

            else:
                favored_model = "TIE"

                interpretation = (
                    f"The two models have identical "
                    f"{metric_name} values."
                )

        evidence[metric_name] = {
            "reference_model": reference_model,
            "reference_value": reference_value,
            "candidate_model": candidate_model,
            "candidate_value": candidate_value,
            "candidate_minus_reference": difference,
            "lower_is_better": True,
            "favored_model": favored_model,
            "deterministic_interpretation": (
                interpretation
            ),
        }

    return evidence


def _summarize_fit_metric_support(
    fit_metrics: Mapping[
        str,
        Mapping[str, object],
    ],
    reference_model: str,
    candidate_model: str,
) -> dict[str, object]:
    """
    Summarize which model is numerically favored across
    the available fit metrics.
    """

    reference_wins: list[str] = []
    candidate_wins: list[str] = []
    ties: list[str] = []
    unavailable: list[str] = []

    for metric_name, metric_result in fit_metrics.items():
        favored_model = metric_result.get(
            "favored_model"
        )

        if favored_model == candidate_model:
            candidate_wins.append(
                metric_name
            )

        elif favored_model == reference_model:
            reference_wins.append(
                metric_name
            )

        elif favored_model == "TIE":
            ties.append(
                metric_name
            )

        else:
            unavailable.append(
                metric_name
            )

    if (
        candidate_wins
        and not reference_wins
    ):
        overall_favored_model: str | None = (
            candidate_model
        )

        deterministic_conclusion = (
            f"{candidate_model} is numerically favored "
            "based on the available lower fit criteria: "
            f"{', '.join(candidate_wins)}."
        )

    elif (
        reference_wins
        and not candidate_wins
    ):
        overall_favored_model = (
            reference_model
        )

        deterministic_conclusion = (
            f"{reference_model} is numerically favored "
            "based on the available lower fit criteria: "
            f"{', '.join(reference_wins)}."
        )

    elif (
        candidate_wins
        and reference_wins
    ):
        overall_favored_model = None

        deterministic_conclusion = (
            "The fit criteria provide mixed numerical "
            f"support. {candidate_model} is favored for "
            f"{', '.join(candidate_wins)}, while "
            f"{reference_model} is favored for "
            f"{', '.join(reference_wins)}."
        )

    else:
        overall_favored_model = None

        deterministic_conclusion = (
            "The available fit criteria do not identify "
            "a numerically favored model."
        )

    return {
        "candidate_favored_metrics": (
            candidate_wins
        ),
        "reference_favored_metrics": (
            reference_wins
        ),
        "tied_metrics": ties,
        "unavailable_metrics": unavailable,
        "overall_numerically_favored_model": (
            overall_favored_model
        ),
        "deterministic_conclusion": (
            deterministic_conclusion
        ),
    }


def _select_best_model_across_metrics(
    model_names: Sequence[str],
    metric_comparison: pd.DataFrame,
) -> dict[str, object]:
    """
    Select one overall numerically favored model from all
    supplied candidate models.

    For OFV, -2LL, AIC, and BIC:

        lower numeric value = numerically favored

    Each metric is evaluated across all available models.

    Example:

        ADDITIVE
        PROPORTIONAL
        COMBINED

    If PROPORTIONAL has the lowest -2LL, AIC, and BIC,
    PROPORTIONAL is selected as the overall numerical winner.
    """

    if len(model_names) < 2:
        raise ValueError(
            "At least two model names are required."
        )

    metric_winners: dict[str, list[str]] = {
        model_name: []
        for model_name in model_names
    }

    metric_values_by_name: dict[
        str,
        dict[str, float],
    ] = {}

    unavailable_metrics: list[str] = []
    tied_metrics: list[str] = []

    for metric_name in MODEL_SELECTION_METRICS:
        available_values: dict[str, float] = {}

        for model_name in model_names:
            metric_value = _get_numeric_metric(
                metric_comparison=metric_comparison,
                model_name=model_name,
                metric_name=metric_name,
            )

            if metric_value is not None:
                available_values[
                    model_name
                ] = metric_value

        metric_values_by_name[
            metric_name
        ] = available_values

        if len(available_values) < 2:
            unavailable_metrics.append(
                metric_name
            )
            continue

        lowest_value = min(
            available_values.values()
        )

        winning_models = [
            model_name
            for model_name, metric_value
            in available_values.items()
            if metric_value == lowest_value
        ]

        if len(winning_models) == 1:
            winning_model = (
                winning_models[0]
            )

            metric_winners[
                winning_model
            ].append(
                metric_name
            )

        else:
            tied_metrics.append(
                metric_name
            )

    metric_win_counts = {
        model_name: len(
            won_metrics
        )
        for model_name, won_metrics
        in metric_winners.items()
    }

    highest_win_count = max(
        metric_win_counts.values(),
        default=0,
    )

    top_models = [
        model_name
        for model_name, win_count
        in metric_win_counts.items()
        if win_count == highest_win_count
    ]

    if (
        highest_win_count > 0
        and len(top_models) == 1
    ):
        overall_favored_model: str | None = (
            top_models[0]
        )

        winning_metrics = metric_winners[
            overall_favored_model
        ]

        deterministic_conclusion = (
            f"{overall_favored_model} is the overall "
            "numerically favored model because it has "
            "the lowest available values for "
            f"{', '.join(winning_metrics)}."
        )

    else:
        overall_favored_model = None

        deterministic_conclusion = (
            "The available model-selection metrics do not "
            "identify one uniquely favored model."
        )

    return {
        "metric_values_by_name": (
            metric_values_by_name
        ),
        "metric_winners_by_model": (
            metric_winners
        ),
        "metric_win_counts": (
            metric_win_counts
        ),
        "tied_metrics": tied_metrics,
        "unavailable_metrics": (
            unavailable_metrics
        ),
        "overall_numerically_favored_model": (
            overall_favored_model
        ),
        "deterministic_conclusion": (
            deterministic_conclusion
        ),
    }


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
    Build provider-independent evidence for any two-model
    comparison.

    No model names are hard-coded.

    Examples include:

        ZERO ORDER vs FIRST ORDER
        FIRST ORDER vs TRANSIT ABSORPTION
        ONE COMP vs TWO COMP
        TWO COMP vs THREE COMP
        LINEAR vs MICHAELIS MENTEN
        MODEL A vs MODEL B
    """

    reference_parameters = set(
        _get_model_parameters(
            parameter_comparison=(
                parameter_comparison
            ),
            model_name=reference_model,
        )
    )

    candidate_parameters = set(
        _get_model_parameters(
            parameter_comparison=(
                parameter_comparison
            ),
            model_name=candidate_model,
        )
    )

    fit_metrics = _build_metric_evidence(
        metric_comparison=metric_comparison,
        reference_model=reference_model,
        candidate_model=candidate_model,
    )

    numerical_summary = (
        _summarize_fit_metric_support(
            fit_metrics=fit_metrics,
            reference_model=reference_model,
            candidate_model=candidate_model,
        )
    )

    reference_success = _get_metric_value(
        metric_comparison=metric_comparison,
        model_name=reference_model,
        possible_names=SUCCESS_METRIC_NAMES,
    )

    candidate_success = _get_metric_value(
        metric_comparison=metric_comparison,
        model_name=candidate_model,
        possible_names=SUCCESS_METRIC_NAMES,
    )

    reference_covariance = _get_metric_value(
        metric_comparison=metric_comparison,
        model_name=reference_model,
        possible_names=COVARIANCE_METRIC_NAMES,
    )

    candidate_covariance = _get_metric_value(
        metric_comparison=metric_comparison,
        model_name=candidate_model,
        possible_names=COVARIANCE_METRIC_NAMES,
    )

    return {
        "review_type": (
            "two_model_comparison"
        ),
        "stage": stage_name,
        "reference_model": reference_model,
        "candidate_model": candidate_model,
        "difference_definition": (
            "All differences are candidate minus reference."
        ),
        "metric_rule": (
            "For OFV, -2LL, AIC, and BIC, the lower "
            "numeric value is treated as numerically "
            "favored, including when values are negative."
        ),
        "fit_metrics": fit_metrics,
        "numerical_summary": numerical_summary,
        "estimation_status": {
            reference_model: _normalize_status(
                reference_success
            ),
            candidate_model: _normalize_status(
                candidate_success
            ),
        },
        "covariance_status": {
            reference_model: _normalize_status(
                reference_covariance
            ),
            candidate_model: _normalize_status(
                candidate_covariance
            ),
        },
        "parameters": {
            "shared": sorted(
                reference_parameters
                & candidate_parameters
            ),
            "unique_to_reference": sorted(
                reference_parameters
                - candidate_parameters
            ),
            "unique_to_candidate": sorted(
                candidate_parameters
                - reference_parameters
            ),
        },
        "gof_images": {
            reference_model: (
                reference_gof_available
            ),
            candidate_model: (
                candidate_gof_available
            ),
        },
        "limitations": [
            (
                "The LLM receives only GOF image "
                "availability and does not visually "
                "interpret the plots."
            ),
            (
                "Parameter plausibility and precision "
                "require human pharmacometric review."
            ),
            (
                "The candidates should use the same "
                "dataset and comparable estimation "
                "settings."
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
    """
    Build provider-independent evidence for residual-error
    model comparison.

    The application currently uses this for:

        ADDITIVE
        PROPORTIONAL
        COMBINED

    The function evaluates pairwise evidence and also selects
    one overall numerical winner across all supplied models.
    """

    if reference_model not in model_names:
        raise ValueError(
            f"Reference model '{reference_model}' is not "
            "included in model_names."
        )

    if len(model_names) < 2:
        raise ValueError(
            "At least two residual-error models are required."
        )

    pairwise_fit_metrics: dict[
        str,
        dict[str, dict[str, object]],
    ] = {}

    pairwise_numerical_summaries: dict[
        str,
        dict[str, object],
    ] = {}

    for candidate_model in model_names:
        if candidate_model == reference_model:
            continue

        comparison_name = (
            f"{candidate_model} minus "
            f"{reference_model}"
        )

        fit_metrics = _build_metric_evidence(
            metric_comparison=metric_comparison,
            reference_model=reference_model,
            candidate_model=candidate_model,
        )

        numerical_summary = (
            _summarize_fit_metric_support(
                fit_metrics=fit_metrics,
                reference_model=reference_model,
                candidate_model=candidate_model,
            )
        )

        pairwise_fit_metrics[
            comparison_name
        ] = fit_metrics

        pairwise_numerical_summaries[
            comparison_name
        ] = numerical_summary

    overall_numerical_summary = (
        _select_best_model_across_metrics(
            model_names=model_names,
            metric_comparison=metric_comparison,
        )
    )

    estimation_status = {
        model_name: _normalize_status(
            _get_metric_value(
                metric_comparison=metric_comparison,
                model_name=model_name,
                possible_names=SUCCESS_METRIC_NAMES,
            )
        )
        for model_name in model_names
    }

    covariance_status = {
        model_name: _normalize_status(
            _get_metric_value(
                metric_comparison=metric_comparison,
                model_name=model_name,
                possible_names=COVARIANCE_METRIC_NAMES,
            )
        )
        for model_name in model_names
    }

    parameters_by_model = {
        model_name: _get_model_parameters(
            parameter_comparison=(
                parameter_comparison
            ),
            model_name=model_name,
        )
        for model_name in model_names
    }

    gof_images = {
        model_name: bool(
            gof_availability.get(
                model_name,
                False,
            )
        )
        for model_name in model_names
    }

    return {
        "review_type": (
            "residual_error_model_comparison"
        ),
        "stage": (
            "Residual Error Model Selection"
        ),
        "models_compared": list(
            model_names
        ),
        "reference_model": reference_model,
        "difference_definition": (
            "All pairwise differences are candidate "
            "minus reference."
        ),
        "metric_rule": (
            "For OFV, -2LL, AIC, and BIC, the lower "
            "numeric value is treated as numerically "
            "favored, including when values are negative."
        ),
        "pairwise_fit_metrics": (
            pairwise_fit_metrics
        ),
        "pairwise_numerical_summaries": (
            pairwise_numerical_summaries
        ),
        "overall_numerical_summary": (
            overall_numerical_summary
        ),
        "estimation_status": (
            estimation_status
        ),
        "covariance_status": (
            covariance_status
        ),
        "parameters_by_model": (
            parameters_by_model
        ),
        "gof_images": gof_images,
        "limitations": [
            (
                "The LLM receives only GOF image "
                "availability and does not visually "
                "interpret the plots."
            ),
            (
                "The final residual-error selection "
                "requires human pharmacometric "
                "confirmation."
            ),
            (
                "Additional complexity should be "
                "justified by parameter estimability "
                "and diagnostic improvement."
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
    """
    Build provider-independent evidence for the final
    selected base model.
    """

    decision = (
        reviewer_decision.strip()
        if reviewer_decision
        else "Not recorded"
    )

    comments = (
        reviewer_comments.strip()
        if reviewer_comments
        else "No reviewer comments provided."
    )

    return {
        "review_type": (
            "final_base_model"
        ),
        "selected_models": {
            "absorption_model": (
                absorption_model
            ),
            "structural_model": (
                structural_model
            ),
            "residual_error_model": (
                residual_error_model
            ),
        },
        "final_model": (
            f"{absorption_model} + "
            f"{structural_model} + "
            f"{residual_error_model}"
        ),
        "reviewer_decision": decision,
        "reviewer_comments": comments,
        "remaining_checks": [
            (
                "Confirm successful minimization."
            ),
            (
                "Confirm covariance-step success."
            ),
            (
                "Confirm parameter precision."
            ),
            (
                "Confirm physiological plausibility."
            ),
            (
                "Confirm acceptable shrinkage."
            ),
            (
                "Confirm absence of systematic "
                "GOF trends."
            ),
            (
                "Confirm that improvement in fit "
                "justifies additional model complexity."
            ),
        ],
    }