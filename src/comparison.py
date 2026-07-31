from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.models import CandidateModel


def validate_candidate_collection(
    candidates: Sequence[CandidateModel],
) -> None:
    """
    Validate a collection of candidate models before comparison.
    """

    if len(candidates) < 2:
        raise ValueError(
            "At least two candidate models are required."
        )

    candidate_names = [
        candidate.name
        for candidate in candidates
    ]

    if len(candidate_names) != len(
        set(candidate_names)
    ):
        raise ValueError(
            "Candidate model names must be unique."
        )


def compare_estimates(
    candidates: Sequence[CandidateModel],
) -> pd.DataFrame:
    """
    Build the parameter-estimate comparison table.

    An outer join is used because candidate models may contain different
    parameters.

    Example:

    ONE COMP:
        tvcl
        tvvc
        tvka

    MICHAELIS MENTEN:
        tvvmax
        tvkm
        tvvc
        tvka

    The final table retains:
        tvcl
        tvvmax
        tvkm
        tvvc
        tvka
    """

    validate_candidate_collection(
        candidates
    )

    comparison: pd.DataFrame | None = None

    for candidate in candidates:
        candidate_table = candidate.estimates[
            [
                "parameter",
        
                "estimate",
            ]
        ].copy()

        candidate_table = candidate_table.rename(
            columns={
      
                "estimate": (
                    f"{candidate.name} Estimate"
                ),
            }
        )

        if comparison is None:
            comparison = candidate_table
        else:
            comparison = comparison.merge(
                candidate_table,
                on="parameter",
                how="outer",
                sort=False,
            )

    if comparison is None:
        raise ValueError(
            "No estimate data were supplied."
        )

    return comparison.reset_index(
        drop=True
    )


def compare_metrics(
    candidates: Sequence[CandidateModel],
) -> pd.DataFrame:
    """
    Build the complete metric comparison table.

    An outer join is used because models may have different metric rows,
    including different numbers of ETA-shrinkage results.
    """

    validate_candidate_collection(
        candidates
    )

    comparison: pd.DataFrame | None = None

    for candidate in candidates:
        value_columns = [
            column
            for column in candidate.metrics.columns
            if column != "Metric"
        ]

        if len(value_columns) != 1:
            raise ValueError(
                f"Metric table for '{candidate.name}' must "
                "contain exactly one model-value column."
            )

        original_value_column = (
            value_columns[0]
        )

        candidate_table = candidate.metrics[
            [
                "Metric",
                original_value_column,
            ]
        ].copy()

        candidate_table = candidate_table.rename(
            columns={
                original_value_column: candidate.name,
            }
        )

        if comparison is None:
            comparison = candidate_table
        else:
            comparison = comparison.merge(
                candidate_table,
                on="Metric",
                how="outer",
                sort=False,
            )

    if comparison is None:
        raise ValueError(
            "No metric data were supplied."
        )

    return comparison.reset_index(
        drop=True
    )


def calculate_metric_differences(
    metric_comparison: pd.DataFrame,
    reference_model: str,
    candidate_model: str,
    selected_metrics: Sequence[str] | None = None,
) -> pd.DataFrame:
    """
    Calculate candidate minus reference differences for shared numeric
    model-selection metrics.

    Typical selected metrics:
        OFV
        -2LL
        AIC
        BIC

    Text rows such as Successful or Likelihood Approximation are ignored.
    """

    required_columns = {
        "Metric",
        reference_model,
        candidate_model,
    }

    missing_columns = (
        required_columns
        - set(metric_comparison.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "Metric comparison is missing columns: "
            f"{missing_text}."
        )

    output = metric_comparison.copy()

    if selected_metrics is not None:
        selected_normalized = {
            str(metric).strip().lower()
            for metric in selected_metrics
        }

        metric_name_normalized = (
            output["Metric"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        output = output[
            metric_name_normalized.isin(
                selected_normalized
            )
        ].copy()

    output[reference_model] = pd.to_numeric(
        output[reference_model],
        errors="coerce",
    )

    output[candidate_model] = pd.to_numeric(
        output[candidate_model],
        errors="coerce",
    )

    output = output.dropna(
        subset=[
            reference_model,
            candidate_model,
        ]
    )

    difference_column = (
        f"{candidate_model} minus {reference_model}"
    )

    output[difference_column] = (
        output[candidate_model]
        - output[reference_model]
    )

    return output.reset_index(
        drop=True
    )