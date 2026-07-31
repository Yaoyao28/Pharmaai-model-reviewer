from pathlib import Path

import pandas as pd

from src.loaders import (
    discover_models,
    find_gof_image,
    format_folder_name,
    normalize_estimate_columns,
    normalize_metric_columns,
)


def test_format_folder_name():
    result = format_folder_name(
        "michaelis_menten"
    )

    assert result == "MICHAELIS MENTEN"


def test_discover_models(
    tmp_path: Path,
):
    stage_folder = (
        tmp_path / "structural"
    )

    stage_folder.mkdir()

    one_comp = (
        stage_folder / "one_comp"
    )

    two_comp = (
        stage_folder / "two_comp"
    )

    one_comp.mkdir()
    two_comp.mkdir()

    result = discover_models(
        stage_folder
    )

    assert set(result) == {
        "one_comp",
        "two_comp",
    }


def test_find_gof_image(
    tmp_path: Path,
):
    model_folder = (
        tmp_path / "one_comp"
    )

    model_folder.mkdir()

    gof_path = (
        model_folder / "gof.png"
    )

    gof_path.write_bytes(
        b"fake-image-content"
    )

    result = find_gof_image(
        model_folder
    )

    assert result == gof_path


def test_missing_gof_returns_none(
    tmp_path: Path,
):
    model_folder = (
        tmp_path / "one_comp"
    )

    model_folder.mkdir()

    result = find_gof_image(
        model_folder
    )

    assert result is None


def test_normalize_estimate_columns():
    table = pd.DataFrame(
        {
            "Parameter": ["tvcl"],
            "Constant": [False],
            "Estimate": [7.18],
        }
    )

    result = normalize_estimate_columns(
        table
    )

    assert list(result.columns) == [
        "parameter",
        "constant",
        "estimate",
    ]


def test_normalize_metric_columns():
    table = pd.DataFrame(
        {
            " metric ": ["AIC"],
            "ONE_COMP": [-100],
        }
    )

    result = normalize_metric_columns(
        table
    )

    assert "Metric" in result.columns