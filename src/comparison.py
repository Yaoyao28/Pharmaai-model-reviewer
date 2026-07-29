from __future__ import annotations

import pandas as pd


def compare_estimates(
    estimate_tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compare parameter estimates across candidate models.

    Expected columns in each input table:
    parameter, constant, estimate

    An outer merge is used so parameters that exist in only one
    model are still retained.
    """

    if not estimate_tables:
        raise ValueError(
            "At least one estimate table is required."
        )

    comparison_df: pd.DataFrame | None = None

    for model_name, estimate_df in estimate_tables.items():
        required_columns = {
            "parameter",
            "constant",
            "estimate",
        }

        missing_columns = (
            required_columns - set(estimate_df.columns)
        )

        if missing_columns:
            raise ValueError(
                f"{model_name} estimate file is missing columns: "
                f"{sorted(missing_columns)}"
            )

        current_df = estimate_df[
            [
                "parameter",
                "constant",
                "estimate",
            ]
        ].copy()

        current_df["parameter"] = (
            current_df["parameter"]
            .astype(str)
            .str.strip()
        )

        current_df = current_df.rename(
            columns={
                "constant": f"{model_name} Constant",
                "estimate": f"{model_name} Estimate",
            }
        )

        if comparison_df is None:
            comparison_df = current_df
        else:
            comparison_df = comparison_df.merge(
                current_df,
                on="parameter",
                how="outer",
            )

    if comparison_df is None:
        return pd.DataFrame()

    return comparison_df.reset_index(drop=True)


def compare_metrics(
    metric_tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Compare model metrics across candidate models.

    Expected input format:
    Metric plus exactly one model-value column.

    Example:
    Metric,ONE_COMP
    AIC,-18021.749
    BIC,-17959.939
    """

    if not metric_tables:
        raise ValueError(
            "At least one metric table is required."
        )

    comparison_df: pd.DataFrame | None = None

    for model_name, metric_df in metric_tables.items():
        if "Metric" not in metric_df.columns:
            raise ValueError(
                f"{model_name} metrics file is missing "
                "the Metric column."
            )

        value_columns = [
            column
            for column in metric_df.columns
            if column != "Metric"
        ]

        if len(value_columns) != 1:
            raise ValueError(
                f"{model_name} metrics file must contain "
                "exactly one value column besides Metric."
            )

        original_value_column = value_columns[0]

        current_df = metric_df[
            [
                "Metric",
                original_value_column,
            ]
        ].copy()

        current_df["Metric"] = (
            current_df["Metric"]
            .astype(str)
            .str.strip()
        )

        current_df = current_df.rename(
            columns={
                original_value_column: model_name,
            }
        )

        if comparison_df is None:
            comparison_df = current_df
        else:
            comparison_df = comparison_df.merge(
                current_df,
                on="Metric",
                how="outer",
            )

    if comparison_df is None:
        return pd.DataFrame()

    return comparison_df.reset_index(drop=True)


def calculate_metric_differences(
    metric_comparison: pd.DataFrame,
    reference_model: str,
    candidate_model: str,
    selected_metrics: list[str] | None = None,
) -> pd.DataFrame:
    """
    Calculate candidate minus reference for selected numeric metrics.

    Example:
    Difference = TWO_COMP - ONE_COMP

    Non-numeric values are excluded automatically.
    """

    required_columns = {
        "Metric",
        reference_model,
        candidate_model,
    }

    missing_columns = (
        required_columns - set(metric_comparison.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing comparison columns: "
            f"{sorted(missing_columns)}"
        )

    difference_df = metric_comparison[
        [
            "Metric",
            reference_model,
            candidate_model,
        ]
    ].copy()

    if selected_metrics is not None:
        difference_df = difference_df[
            difference_df["Metric"].isin(selected_metrics)
        ].copy()

    difference_df[reference_model] = pd.to_numeric(
        difference_df[reference_model],
        errors="coerce",
    )

    difference_df[candidate_model] = pd.to_numeric(
        difference_df[candidate_model],
        errors="coerce",
    )

    difference_df = difference_df.dropna(
        subset=[
            reference_model,
            candidate_model,
        ]
    )

    difference_column = (
        f"Δ ({candidate_model} - {reference_model})"
    )

    difference_df[difference_column] = (
        difference_df[candidate_model]
        - difference_df[reference_model]
    )

    return difference_df[
        [
            "Metric",
            reference_model,
            candidate_model,
            difference_column,
        ]
    ].reset_index(drop=True)