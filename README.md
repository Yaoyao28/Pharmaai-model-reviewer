# PharmaAI Model Reviewer

AI-assisted Population PK Model Reviewer

## Goal

Build an AI application that helps pharmacometricians compare
Population PK models and generate AI-assisted review reports.

## Features

- Configuration-driven model comparison
- Parameter estimate comparison
- Model metric comparison
- Automatic metric difference calculation
- Rule-based model recommendation
- Diagnostic plot comparison
- Input validation
- Unit testing

## Supported Comparisons

- One-compartment vs two-compartment
- Zero-order vs first-order absorption

## Model Recommendation Logic

The application compares candidate and reference models using
AIC, BIC, and OFV. Lower values favor the corresponding model.
The recommendation is intended to support, not replace,
scientific review of diagnostics and parameter plausibility.


A lower objective function or information criterion alone does not    
establish that a model is scientifically appropriate. Diagnostic
plots, parameter plausibility, model stability, and intended use
must also be considered.


## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- OpenAI API