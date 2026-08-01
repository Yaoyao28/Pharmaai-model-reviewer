from __future__ import annotations

from datetime import datetime
from typing import Any


def _nested_value(
    data: dict[str, Any] | None,
    *keys: str,
) -> Any:
    """Safely read a nested dictionary value."""

    current: Any = data

    for key in keys:
        if not isinstance(current, dict):
            return None

        current = current.get(key)

        if current is None:
            return None

    return current


def _clean_text(
    value: object | None,
    default: str,
) -> str:
    """Convert an optional value to report-ready text."""

    if value is None:
        return default

    cleaned = str(value).strip()

    return cleaned or default


def _build_stage_section(
    stage_name: str,
    selected_model: str | None,
    evidence: dict[str, Any] | None,
    llm_review: str | None,
) -> dict[str, Any]:
    """Build one standardized report section."""

    two_model_favored = _nested_value(
        evidence,
        "numerical_summary",
        "overall_numerically_favored_model",
    )

    residual_favored = _nested_value(
        evidence,
        "overall_numerical_summary",
        "overall_numerically_favored_model",
    )

    two_model_conclusion = _nested_value(
        evidence,
        "numerical_summary",
        "deterministic_conclusion",
    )

    residual_conclusion = _nested_value(
        evidence,
        "overall_numerical_summary",
        "deterministic_conclusion",
    )

    return {
        "stage_name": stage_name,
        "selected_model": _clean_text(
            selected_model,
            "Not selected",
        ),
        "numerically_favored_model": _clean_text(
            residual_favored or two_model_favored,
            "Not determined",
        ),
        "deterministic_conclusion": _clean_text(
            residual_conclusion or two_model_conclusion,
            "No deterministic conclusion was recorded.",
        ),
        "llm_review": _clean_text(
            llm_review,
            "No LLM review was generated.",
        ),
    }


def build_final_report(
    selected_absorption_model: str | None,
    selected_structural_model: str | None,
    selected_error_model: str | None,
    absorption_evidence: dict[str, Any] | None = None,
    absorption_llm_review: str | None = None,
    structural_evidence: dict[str, Any] | None = None,
    structural_llm_review: str | None = None,
    residual_error_evidence: dict[str, Any] | None = None,
    residual_error_llm_review: str | None = None,
    llm_provider: str | None = None,
    llm_model: str | None = None,
) -> dict[str, Any]:
    """Build the provider-independent final report dictionary."""

    generated_at = datetime.now().astimezone()

    absorption_section = _build_stage_section(
        stage_name="Absorption Model Selection",
        selected_model=selected_absorption_model,
        evidence=absorption_evidence,
        llm_review=absorption_llm_review,
    )

    structural_section = _build_stage_section(
        stage_name="Structural Model Selection",
        selected_model=selected_structural_model,
        evidence=structural_evidence,
        llm_review=structural_llm_review,
    )

    residual_section = _build_stage_section(
        stage_name="Residual Error Model Selection",
        selected_model=selected_error_model,
        evidence=residual_error_evidence,
        llm_review=residual_error_llm_review,
    )

    final_model = " + ".join(
        [
            absorption_section["selected_model"],
            structural_section["selected_model"],
            residual_section["selected_model"],
        ]
    )

    return {
        "report_title": "PharmaAI Model Review Report",
        "generated_at": generated_at.isoformat(
            timespec="seconds"
        ),
        "generated_at_display": generated_at.strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        ),
        "report_status": (
            "AI-assisted draft with human-confirmed model selections"
        ),
        "llm_provider": _clean_text(
            llm_provider,
            "Not recorded",
        ),
        "llm_model": _clean_text(
            llm_model,
            "Not recorded",
        ),
        "selected_models": {
            "absorption_model": absorption_section[
                "selected_model"
            ],
            "structural_model": structural_section[
                "selected_model"
            ],
            "residual_error_model": residual_section[
                "selected_model"
            ],
        },
        "final_model": final_model,
        "sections": [
            absorption_section,
            structural_section,
            residual_section,
        ],
        "audit_statement": (
            "Numerical comparisons were performed deterministically "
            "by the application. The LLM generated narrative text "
            "from structured evidence. Final model selections were "
            "confirmed by the human reviewer."
        ),
        "limitations": [
            (
                "The LLM did not visually interpret goodness-of-fit "
                "images."
            ),
            (
                "The report does not replace review of convergence, "
                "covariance results, parameter precision, shrinkage, "
                "model stability, or scientific plausibility."
            ),
            (
                "Candidate models should use the same dataset and "
                "comparable estimation settings."
            ),
        ],
    }