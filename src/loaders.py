from __future__ import annotations

from pathlib import Path

import pandas as pd


SUPPORTED_TABLE_EXTENSIONS = (
    ".xlsx",
    ".xls",
    ".csv",
)

SUPPORTED_IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
)


def format_folder_name(
    folder_name: str,
) -> str:
    """
    Convert a folder name into a user-facing model name.

    Examples:
        one_comp -> ONE COMP
        two_comp -> TWO COMP
        michaelis_menten -> MICHAELIS MENTEN
    """

    return (
        folder_name
        .replace("_", " ")
        .strip()
        .upper()
    )


def discover_models(
    stage_folder: str | Path,
) -> dict[str, Path]:
    """
    Discover model folders under one workflow stage.
    """

    stage_path = Path(stage_folder)

    if not stage_path.exists():
        return {}

    if not stage_path.is_dir():
        return {}

    discovered = {
        child.name: child
        for child in stage_path.iterdir()
        if child.is_dir()
        and not child.name.startswith(".")
        and not child.name.startswith("__")
    }

    return dict(
        sorted(discovered.items())
    )


def find_model_table(
    model_folder: str | Path,
    file_stem: str,
) -> Path:
    """
    Find estimates.xlsx, metrics.xlsx, or CSV equivalents.
    """

    folder = Path(model_folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"Model folder does not exist: {folder}"
        )

    for extension in SUPPORTED_TABLE_EXTENSIONS:
        candidate_path = (
            folder / f"{file_stem}{extension}"
        )

        if candidate_path.exists():
            return candidate_path

    expected_files = ", ".join(
        f"{file_stem}{extension}"
        for extension in SUPPORTED_TABLE_EXTENSIONS
    )

    raise FileNotFoundError(
        f"Could not find '{file_stem}' in '{folder}'. "
        f"Expected one of: {expected_files}."
    )


def find_gof_image(
    model_folder: str | Path,
) -> Path | None:
    """
    Find the optional combined GOF image for one model.

    Supported filenames:
        gof.png
        gof.jpg
        gof.jpeg
    """

    folder = Path(model_folder)

    if not folder.exists():
        return None

    for extension in SUPPORTED_IMAGE_EXTENSIONS:
        candidate_path = folder / f"gof{extension}"

        if candidate_path.exists():
            return candidate_path

    return None


def read_table(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Read an Excel or CSV table.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    extension = path.suffix.lower()

    if extension in {
        ".xlsx",
        ".xls",
    }:
        return pd.read_excel(path)

    if extension == ".csv":
        return pd.read_csv(path)

    raise ValueError(
        f"Unsupported table type: {extension}"
    )


def normalize_estimate_columns(
    table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize estimate-table columns.

    Expected columns:
        parameter
        constant
        estimate
    """

    normalized = table.copy()

    normalized.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        for column in normalized.columns
    ]

    return normalized


def normalize_metric_columns(
    table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize the Metric column while preserving the model-value column.
    """

    normalized = table.copy()

    rename_map: dict[object, str] = {}

    for column in normalized.columns:
        normalized_name = (
            str(column)
            .strip()
            .lower()
        )

        if normalized_name == "metric":
            rename_map[column] = "Metric"

    return normalized.rename(
        columns=rename_map
    )


def load_estimate_table(
    source: str | Path,
) -> pd.DataFrame:
    """
    Load and normalize an estimate table.
    """

    table = read_table(source)

    return normalize_estimate_columns(
        table
    )


def load_metric_table(
    source: str | Path,
) -> pd.DataFrame:
    """
    Load and normalize a metric table.
    """

    table = read_table(source)

    return normalize_metric_columns(
        table
    )