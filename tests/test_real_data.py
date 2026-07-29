import pandas as pd

from src.comparison import (
    calculate_metric_differences,
    compare_estimates,
    compare_metrics,
)
from src.validation import (
    validate_estimate_table,
    validate_metric_table,
)


REFERENCE_MODEL = "ONE_COMP"
CANDIDATE_MODEL = "TWO_COMP"


estimates_1 = pd.read_excel(
    "data/demo/compartment/model_1/estimates_1comp.xlsx",
    sheet_name="ONE_COMP",
)

metrics_1 = pd.read_excel(
    "data/demo/compartment/model_1/metrics_1comp.xlsx",
    sheet_name="ONE_COMP",
)

estimates_2 = pd.read_excel(
    "data/demo/compartment/model_2/estimates_2comp.xlsx",
    sheet_name="TWO_COMP",
)

metrics_2 = pd.read_excel(
    "data/demo/compartment/model_2/metrics_2comp.xlsx",
    sheet_name="TWO_COMP",
)


validate_estimate_table(
    estimates_1,
    REFERENCE_MODEL,
)

validate_estimate_table(
    estimates_2,
    CANDIDATE_MODEL,
)

validate_metric_table(
    metrics_1,
    REFERENCE_MODEL,
)

validate_metric_table(
    metrics_2,
    CANDIDATE_MODEL,
)


estimate_comparison = compare_estimates(
    {
        REFERENCE_MODEL: estimates_1,
        CANDIDATE_MODEL: estimates_2,
    }
)

metric_comparison = compare_metrics(
    {
        REFERENCE_MODEL: metrics_1,
        CANDIDATE_MODEL: metrics_2,
    }
)

selected_metrics = [
    "-2LL",
    "AIC",
    "BIC",
    "Estimation Time",
    "Optimized Parameters",
    "(η-shrinkage) η₁",
    "(η-shrinkage) η₂",
    "(η-shrinkage) η₃",
    "(η-shrinkage) η₄",
    "(η-shrinkage) η₅",
    "(ε-shrinkage) conc",
]

metric_differences = calculate_metric_differences(
    metric_comparison=metric_comparison,
    reference_model=REFERENCE_MODEL,
    candidate_model=CANDIDATE_MODEL,
    selected_metrics=selected_metrics,
)


print("\nESTIMATE COMPARISON")
print(
    estimate_comparison.to_string(
        index=False
    )
)

print("\nMETRIC COMPARISON")
print(
    metric_comparison.to_string(
        index=False
    )
)

print("\nSELECTED METRIC DIFFERENCES")
print(
    metric_differences.to_string(
        index=False
    )
)