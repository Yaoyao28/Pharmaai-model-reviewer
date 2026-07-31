import pytest

from src.workflow import (
    create_final_model_summary,
    normalize_model_name,
)


def test_normalize_model_name():
    result = normalize_model_name(
        "  MICHAELIS MENTEN  "
    )

    assert result == (
        "MICHAELIS MENTEN"
    )


def test_empty_model_name_raises_error():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        normalize_model_name(
            "   "
        )


def test_create_final_model_summary():
    result = create_final_model_summary(
        absorption_model=(
            "FIRST ORDER"
        ),
        structural_model=(
            "MICHAELIS MENTEN"
        ),
        residual_error_model=(
            "COMBINED"
        ),
    )

    assert result == {
        "absorption_model": (
            "FIRST ORDER"
        ),
        "structural_model": (
            "MICHAELIS MENTEN"
        ),
        "residual_error_model": (
            "COMBINED"
        ),
    }