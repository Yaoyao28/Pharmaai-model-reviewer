from src.decision import recommend_model


def test_candidate_is_selected_when_metrics_are_lower():
    differences = {
        "AIC": -20.0,
        "BIC": -15.0,
        "OFV": -25.0,
    }

    result = recommend_model(
        differences,
        reference_model="ONE_COMP",
        candidate_model="TWO_COMP",
    )

    assert result["preferred_model"] == "TWO_COMP"