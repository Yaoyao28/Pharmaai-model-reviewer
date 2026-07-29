from __future__ import annotations

import pandas as pd


ESTIMATE_REQUIRED_COLUMNS = {
    "parameter",
    "constant",
    "estimate",
}


def validate_estimate_table(
    estimate_df: pd.DataFrame,
    model_name: str,
) -> None:
    """
    Validate one parameter-estimate table.
    """

    if estimate_df.empty:
        raise ValueError(
            f"{model_name} estimate table is empty."
        )

    missing_columns = (
        ESTIMATE_REQUIRED_COLUMNS
        - set(estimate_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{model_name} estimate table is missing columns: "
            f"{sorted(missing_columns)}"
        )

    parameter_names = (
        estimate_df["parameter"]
        .astype(str)
        .str.strip()
    )

    if parameter_names.eq("").any():
        raise ValueError(
            f"{model_name} estimate table contains "
            "a blank parameter name."
        )

    duplicated_parameters = parameter_names[
        parameter_names.duplicated()
    ].tolist()

    if duplicated_parameters:
        raise ValueError(
            f"{model_name} estimate table contains duplicate "
            f"parameters: {duplicated_parameters}"
        )


def validate_metric_table(
    metric_df: pd.DataFrame,
    model_name: str,
) -> None:
    """
    Validate one model-metrics table.
    """

    if metric_df.empty:
        raise ValueError(
            f"{model_name} metrics table is empty."
        )

    if "Metric" not in metric_df.columns:
        raise ValueError(
            f"{model_name} metrics table is missing "
            "the Metric column."
        )

    value_columns = [
        column
        for column in metric_df.columns
        if column != "Metric"
    ]

    if len(value_columns) != 1:
        raise ValueError(
            f"{model_name} metrics table must contain "
            "exactly one value column besides Metric."
        )

    metric_names = (
        metric_df["Metric"]
        .astype(str)
        .str.strip()
    )

    if metric_names.eq("").any():
        raise ValueError(
            f"{model_name} metrics table contains "
            "a blank metric name."
        )

    duplicated_metrics = metric_names[
        metric_names.duplicated()
    ].tolist()

    if duplicated_metrics:
        raise ValueError(
            f"{model_name} metrics table contains duplicate "
            f"metrics: {duplicated_metrics}"
        )