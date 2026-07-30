import pandas as pd
import pytest

from src.validation import (
    validate_estimate_table,
    validate_metric_table,
)


def test_valid_estimate_table():
    estimate_df = pd.DataFrame(
        {
            "parameter": ["CL", "V"],
            "constant": [False, False],
            "estimate": [10.0, 50.0],
        }
    )

    validate_estimate_table(
        estimate_df,
        model_name="ONE_COMP",
    )


def test_empty_estimate_table_raises_error():
    estimate_df = pd.DataFrame(
        columns=["parameter", "constant", "estimate"]
    )

    with pytest.raises(
        ValueError,
        match="ONE_COMP estimate table is empty",
    ):
        validate_estimate_table(
            estimate_df,
            model_name="ONE_COMP",
        )


def test_missing_estimate_column_raises_error():
    estimate_df = pd.DataFrame(
        {
            "parameter": ["CL"],
            "estimate": [10.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing columns",
    ):
        validate_estimate_table(
            estimate_df,
            model_name="ONE_COMP",
        )


def test_blank_parameter_name_raises_error():
    estimate_df = pd.DataFrame(
        {
            "parameter": ["CL", "   "],
            "constant": [False, False],
            "estimate": [10.0, 50.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="blank parameter name",
    ):
        validate_estimate_table(
            estimate_df,
            model_name="ONE_COMP",
        )


def test_duplicate_parameter_raises_error():
    estimate_df = pd.DataFrame(
        {
            "parameter": ["CL", "CL"],
            "constant": [False, False],
            "estimate": [10.0, 11.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate parameters",
    ):
        validate_estimate_table(
            estimate_df,
            model_name="ONE_COMP",
        )


def test_valid_metric_table():
    metric_df = pd.DataFrame(
        {
            "Metric": ["OFV", "AIC", "BIC"],
            "ONE_COMP": [100.0, 110.0, 120.0],
        }
    )

    validate_metric_table(
        metric_df,
        model_name="ONE_COMP",
    )


def test_empty_metric_table_raises_error():
    metric_df = pd.DataFrame(
        columns=["Metric", "ONE_COMP"]
    )

    with pytest.raises(
        ValueError,
        match="ONE_COMP metrics table is empty",
    ):
        validate_metric_table(
            metric_df,
            model_name="ONE_COMP",
        )


def test_missing_metric_column_raises_error():
    metric_df = pd.DataFrame(
        {
            "WrongColumn": ["OFV"],
            "ONE_COMP": [100.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing the Metric column",
    ):
        validate_metric_table(
            metric_df,
            model_name="ONE_COMP",
        )


def test_multiple_metric_value_columns_raise_error():
    metric_df = pd.DataFrame(
        {
            "Metric": ["OFV"],
            "ONE_COMP": [100.0],
            "ExtraColumn": [101.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="exactly one value column",
    ):
        validate_metric_table(
            metric_df,
            model_name="ONE_COMP",
        )


def test_blank_metric_name_raises_error():
    metric_df = pd.DataFrame(
        {
            "Metric": ["OFV", "   "],
            "ONE_COMP": [100.0, 110.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="blank metric name",
    ):
        validate_metric_table(
            metric_df,
            model_name="ONE_COMP",
        )


def test_duplicate_metric_raises_error():
    metric_df = pd.DataFrame(
        {
            "Metric": ["AIC", "AIC"],
            "ONE_COMP": [110.0, 111.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate metrics",
    ):
        validate_metric_table(
            metric_df,
            model_name="ONE_COMP",
        )