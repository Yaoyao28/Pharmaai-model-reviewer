import pandas as pd

from src.comparison import (
    calculate_metric_differences,
    compare_estimates,
    compare_metrics,
)
from src.models import CandidateModel


def create_candidate(
    name: str,
    parameters: list[str],
    estimates: list[float],
    metric_names: list[str],
    metric_values: list[object],
) -> CandidateModel:
    estimate_table = pd.DataFrame(
        {
            "parameter": parameters,
            "constant": [
                False
                for _ in parameters
            ],
            "estimate": estimates,
        }
    )

    metric_table = pd.DataFrame(
        {
            "Metric": metric_names,
            name: metric_values,
        }
    )

    return CandidateModel(
        name=name,
        estimates=estimate_table,
        metrics=metric_table,
    )


def test_compare_one_comp_vs_two_comp():
    one_comp = create_candidate(
        name="ONE COMP",
        parameters=[
            "tvcl",
            "tvvc",
            "tvka",
        ],
        estimates=[
            7.18,
            77.0,
            4.16,
        ],
        metric_names=[
            "-2LL",
            "AIC",
            "BIC",
            "(η-shrinkage) η1",
        ],
        metric_values=[
            -18039,
            -18021,
            -17959,
            0.17,
        ],
    )

    two_comp = create_candidate(
        name="TWO COMP",
        parameters=[
            "tvcl",
            "tvvc",
            "tvvp",
            "tvq",
            "tvka",
        ],
        estimates=[
            7.10,
            50.0,
            30.0,
            2.0,
            4.20,
        ],
        metric_names=[
            "-2LL",
            "AIC",
            "BIC",
            "(η-shrinkage) η1",
            "(η-shrinkage) η2",
        ],
        metric_values=[
            -18100,
            -18076,
            -17990,
            0.14,
            0.20,
        ],
    )

    parameter_result = compare_estimates(
        [
            one_comp,
            two_comp,
        ]
    )

    metric_result = compare_metrics(
        [
            one_comp,
            two_comp,
        ]
    )

    assert "tvvp" in (
        parameter_result[
            "parameter"
        ].tolist()
    )

    assert "(η-shrinkage) η2" in (
        metric_result[
            "Metric"
        ].tolist()
    )


def test_compare_one_comp_vs_michaelis_menten():
    one_comp = create_candidate(
        name="ONE COMP",
        parameters=[
            "tvcl",
            "tvvc",
            "tvka",
        ],
        estimates=[
            7.18,
            77.0,
            4.16,
        ],
        metric_names=[
            "-2LL",
            "AIC",
            "BIC",
        ],
        metric_values=[
            -18039,
            -18021,
            -17959,
        ],
    )

    michaelis_menten = create_candidate(
        name="MICHAELIS MENTEN",
        parameters=[
            "tvvmax",
            "tvkm",
            "tvvc",
            "tvka",
        ],
        estimates=[
            20.0,
            2.0,
            75.0,
            4.10,
        ],
        metric_names=[
            "-2LL",
            "AIC",
            "BIC",
            "(η-shrinkage) η1",
            "(η-shrinkage) η2",
            "(η-shrinkage) η3",
        ],
        metric_values=[
            -18120,
            -18098,
            -18010,
            0.10,
            0.12,
            0.18,
        ],
    )

    parameter_result = compare_estimates(
        [
            one_comp,
            michaelis_menten,
        ]
    )

    metric_result = compare_metrics(
        [
            one_comp,
            michaelis_menten,
        ]
    )

    parameter_names = (
        parameter_result[
            "parameter"
        ].tolist()
    )

    assert "tvcl" in parameter_names
    assert "tvvmax" in parameter_names
    assert "tvkm" in parameter_names

    assert "(η-shrinkage) η3" in (
        metric_result[
            "Metric"
        ].tolist()
    )


def test_metric_differences():
    metric_comparison = pd.DataFrame(
        {
            "Metric": [
                "-2LL",
                "AIC",
                "BIC",
                "Successful",
            ],
            "ONE COMP": [
                -18039,
                -18021,
                -17959,
                True,
            ],
            "MICHAELIS MENTEN": [
                -18120,
                -18098,
                -18010,
                True,
            ],
        }
    )

    result = calculate_metric_differences(
        metric_comparison=metric_comparison,
        reference_model="ONE COMP",
        candidate_model=(
            "MICHAELIS MENTEN"
        ),
        selected_metrics=[
            "-2LL",
            "AIC",
            "BIC",
        ],
    )

    assert len(result) == 3

    assert (
        "MICHAELIS MENTEN minus ONE COMP"
        in result.columns
    )