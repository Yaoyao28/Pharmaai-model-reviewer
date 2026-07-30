from typing import Any


def recommend_model(
    metric_differences: dict[str, float],
    reference_model: str,
    candidate_model: str,
) -> dict[str, Any]:
    """
    Recommend a model based on model-selection metrics.

    Metric differences are calculated as:
    candidate - reference
    """

    score = 0
    reasons: list[str] = []

    for metric in ["AIC", "BIC", "OFV"]:
        difference = metric_differences.get(metric)

        if difference is None:
            continue

        if difference < 0:
            score += 1
            reasons.append(
                f"{candidate_model} has a lower {metric} "
                f"by {abs(difference):.2f}."
            )
        elif difference > 0:
            score -= 1
            reasons.append(
                f"{reference_model} has a lower {metric} "
                f"by {difference:.2f}."
            )
        else:
            reasons.append(f"The models have the same {metric}.")

    if score > 0:
        preferred_model = candidate_model
    elif score < 0:
        preferred_model = reference_model
    else:
        preferred_model = "No clear preference"

    return {
        "preferred_model": preferred_model,
        "score": score,
        "reasons": reasons,
    }