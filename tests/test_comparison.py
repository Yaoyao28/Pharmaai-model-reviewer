import pandas as pd

from src.comparison import compare_estimates


def test_compare_estimates_uses_outer_join():
    reference = pd.DataFrame(
        {
            "parameter": ["CL", "V"],
            "constant": [False, False],
            "estimate": [10.0, 50.0],
        }
    )

    candidate = pd.DataFrame(
        {
            "parameter": ["CL", "V", "Q"],
            "constant": [False, False, False],
            "estimate": [9.0, 45.0, 5.0],
        }
    )

    result = compare_estimates(
        {
            "ONE_COMP": reference,
            "TWO_COMP": candidate,
        }
    )

    assert "Q" in result["parameter"].values
    assert len(result) == 3

    assert "ONE_COMP Estimate" in result.columns
    assert "TWO_COMP Estimate" in result.columns