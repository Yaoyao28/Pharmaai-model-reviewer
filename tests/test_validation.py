import pandas as pd
import pytest

from src.validation import (
    validate_estimate_table,
    validate_metric_table,
)


def test_validate_estimate_table():
    table = pd.DataFrame(
        {
            "parameter": [
                "tvcl",
                "tvvc",
            ],
            "constant": [
                False,
                False,
            ],
            "estimate": [
                7.18,
                77.0,
            ],
        }
    )

    result = validate_estimate_table(
        table,
        model_name="ONE COMP",
    )

    assert len(result) == 2


def test_michaelis_menten_parameters_are_allowed():
    table = pd.DataFrame(
        {
            "parameter": [
                "tvvmax",
                "tvkm",
                "tvvc",
            ],
            "constant": [
                False,
                False,
                False,
            ],
            "estimate": [
                20.0,
                2.0,
                75.0,
            ],
        }
    )

    result = validate_estimate_table(
        table,
        model_name="MICHAELIS MENTEN",
    )

    assert set(
        result["parameter"]
    ) == {
        "tvvmax",
        "tvkm",
        "tvvc",
    }


def test_duplicate_parameters_raise_error():
    table = pd.DataFrame(
        {
            "parameter": [
                "tvcl",
                "tvcl",
            ],
            "constant": [
                False,
                False,
            ],
            "estimate": [
                7.18,
                7.20,
            ],
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate parameters",
    ):
        validate_estimate_table(
            table,
            model_name="ONE COMP",
        )


def test_metric_table_accepts_text_and_numbers():
    table = pd.DataFrame(
        {
            "Metric": [
                "Successful",
                "Likelihood Approximation",
                "AIC",
                "BIC",
            ],
            "ONE_COMP": [
                True,
                "FOCE",
                -18021.749,
                -17959.939,
            ],
        }
    )

    result = validate_metric_table(
        table,
        model_name="ONE COMP",
    )

    assert len(result) == 4


def test_different_shrinkage_rows_are_allowed():
    table = pd.DataFrame(
        {
            "Metric": [
                "AIC",
                "BIC",
                "(η-shrinkage) η1",
                "(η-shrinkage) η2",
                "(η-shrinkage) η3",
                "(η-shrinkage) η4",
            ],
            "TWO_COMP": [
                -18100,
                -18020,
                0.10,
                0.08,
                0.15,
                0.20,
            ],
        }
    )

    result = validate_metric_table(
        table,
        model_name="TWO COMP",
    )

    assert len(result) == 6