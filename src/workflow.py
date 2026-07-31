from __future__ import annotations

from dataclasses import dataclass
from typing import Final


ABSORPTION_STAGE: Final[str] = (
    "absorption"
)

STRUCTURAL_STAGE: Final[str] = (
    "structural"
)

ERROR_STAGE: Final[str] = (
    "residual_error"
)


@dataclass(frozen=True)
class StageDefinition:
    stage_id: str
    display_name: str
    description: str
    optional: bool


STAGE_DEFINITIONS: Final[
    dict[str, StageDefinition]
] = {
    ABSORPTION_STAGE: StageDefinition(
        stage_id=ABSORPTION_STAGE,
        display_name=(
            "Absorption Model Selection"
        ),
        description=(
            "Compare candidate absorption models while the "
            "remaining model components are held constant."
        ),
        optional=True,
    ),
    STRUCTURAL_STAGE: StageDefinition(
        stage_id=STRUCTURAL_STAGE,
        display_name=(
            "Structural Model Selection"
        ),
        description=(
            "Compare candidate structural models using the "
            "selected or fixed absorption model."
        ),
        optional=False,
    ),
    ERROR_STAGE: StageDefinition(
        stage_id=ERROR_STAGE,
        display_name=(
            "Residual Error Model Selection"
        ),
        description=(
            "Compare residual-error models while the selected "
            "absorption and structural models are held constant."
        ),
        optional=False,
    ),
}


def normalize_model_name(
    model_name: str,
) -> str:
    """
    Validate and clean a model name.
    """

    if not isinstance(model_name, str):
        raise TypeError(
            "Model name must be a string."
        )

    normalized = model_name.strip()

    if not normalized:
        raise ValueError(
            "Model name cannot be empty."
        )

    return normalized


def create_final_model_summary(
    absorption_model: str,
    structural_model: str,
    residual_error_model: str,
) -> dict[str, str]:
    """
    Create a final base-model summary.
    """

    return {
        "absorption_model": normalize_model_name(
            absorption_model
        ),
        "structural_model": normalize_model_name(
            structural_model
        ),
        "residual_error_model": normalize_model_name(
            residual_error_model
        ),
    }