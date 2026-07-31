# PharmaAI Model Reviewer

A Streamlit application for sequential pharmacometric model review.

## Workflow

1. Optional absorption-model comparison
2. Structural-model comparison
3. Residual-error-model comparison
4. Final base-model summary

## Supported comparisons

Candidate model names are discovered from folders rather than hard-coded.

Examples:

- ZERO ORDER vs FIRST ORDER
- ONE COMP vs TWO COMP
- ONE COMP vs MICHAELIS MENTEN
- TWO COMP vs MICHAELIS MENTEN
- ADDITIVE vs PROPORTIONAL
- PROPORTIONAL vs COMBINED

## Model folder structure

Each model folder contains:

```text
model_folder/
├── estimates.xlsx
├── metrics.xlsx
└── gof.png