from __future__ import annotations

import pandas as pd


def validate_estimate_table(
    estimate_table: pd.DataFrame,
    model_name: str | None = None,
) -> pd.DataFrame:
    """
    Validate one candidate model's estimate table.

    Required columns:
        parameter
        constant
        estimate

    Different models may have different:
        parameters;
        OMEGA terms;
        SIGMA terms;
        numbers of rows.

    model_name is optional to remain compatible with older function calls.
    """

    model_label = (
        f" for '{model_name}'"
        if model_name
        else ""
    )

    if estimate_table.empty:
        raise ValueError(
            f"The estimate table{model_label} is empty."
        )

    required_columns = {
        "parameter",
        "constant",
        "estimate",
    }

    missing_columns = (
        required_columns
        - set(estimate_table.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"Estimate table{model_label} is missing "
            f"required columns: {missing_text}."
        )

    validated = estimate_table[
        [
            "parameter",
            "constant",
            "estimate",
        ]
    ].copy()

    validated["parameter"] = (
        validated["parameter"]
        .astype("string")
        .str.strip()
    )

    empty_parameter_mask = (
        validated["parameter"].isna()
        | validated["parameter"].eq("")
    )

    if empty_parameter_mask.any():
        raise ValueError(
            f"Estimate table{model_label} contains "
            "an empty parameter name."
        )

    duplicate_mask = (
        validated["parameter"]
        .duplicated(keep=False)
    )

    if duplicate_mask.any():
        duplicates = (
            validated.loc[
                duplicate_mask,
                "parameter",
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Estimate table{model_label} contains "
            "duplicate parameters: "
            + ", ".join(duplicates)
        )

    validated["estimate"] = pd.to_numeric(
        validated["estimate"],
        errors="coerce",
    )

    invalid_estimate_mask = (
        validated["estimate"].isna()
    )

    if invalid_estimate_mask.any():
        invalid_parameters = (
            validated.loc[
                invalid_estimate_mask,
                "parameter",
            ]
            .dropna()
            .astype(str)
            .tolist()
        )

        raise ValueError(
            f"Estimate table{model_label} contains missing "
            "or nonnumeric estimates for: "
            + ", ".join(invalid_parameters)
        )

    return validated.reset_index(
        drop=True
    )


def validate_metric_table(
    metric_table: pd.DataFrame,
    model_name: str | None = None,
) -> pd.DataFrame:
    """
    Validate one candidate model's metric table.

    Required format:
        Metric | one model-value column

    Metric values may be:
        numeric;
        TRUE/FALSE;
        text;
        likelihood-approximation descriptions;
        shrinkage values.

    Different models may contain different numbers of metric rows.
    """

    model_label = (
        f" for '{model_name}'"
        if model_name
        else ""
    )

    if metric_table.empty:
        raise ValueError(
            f"The metric table{model_label} is empty."
        )

    if "Metric" not in metric_table.columns:
        raise ValueError(
            f"Metric table{model_label} must contain "
            "a 'Metric' column."
        )

    value_columns = [
        column
        for column in metric_table.columns
        if column != "Metric"
    ]

    if len(value_columns) != 1:
        raise ValueError(
            f"Metric table{model_label} must contain exactly "
            "one model-value column in addition to 'Metric'."
        )

    value_column = value_columns[0]

    validated = metric_table[
        [
            "Metric",
            value_column,
        ]
    ].copy()

    validated["Metric"] = (
        validated["Metric"]
        .astype("string")
        .str.strip()
    )

    empty_metric_mask = (
        validated["Metric"].isna()
        | validated["Metric"].eq("")
    )

    if empty_metric_mask.any():
        raise ValueError(
            f"Metric table{model_label} contains "
            "an empty metric name."
        )

    duplicate_mask = (
        validated["Metric"]
        .duplicated(keep=False)
    )

    if duplicate_mask.any():
        duplicates = (
            validated.loc[
                duplicate_mask,
                "Metric",
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Metric table{model_label} contains "
            "duplicate metrics: "
            + ", ".join(duplicates)
        )

    return validated.reset_index(
        drop=True
    )