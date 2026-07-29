import pandas as pd

from src.validation import validate_model_summary

# Read the sample CSV
df = pd.read_csv("data/model_summary.csv")

# Validate
errors = validate_model_summary(df)

# Print result
if errors:
    print("Validation Failed")
    for error in errors:
        print("-", error)
else:
    print("Validation Passed")