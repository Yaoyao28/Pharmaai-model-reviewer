from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd
import streamlit as st

from src.comparison import (
    calculate_metric_differences,
    compare_estimates,
    compare_metrics,
)
from src.loaders import (
    discover_models,
    find_gof_image,
    find_model_table,
    format_folder_name,
    load_estimate_table,
    load_metric_table,
)
from src.models import CandidateModel
from src.validation import (
    validate_estimate_table,
    validate_metric_table,
)
from src.workflow import (
    ABSORPTION_STAGE,
    ERROR_STAGE,
    STRUCTURAL_STAGE,
    STAGE_DEFINITIONS,
    create_final_model_summary,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ABSORPTION_DATA_DIR = DATA_DIR / "absorption"
STRUCTURAL_DATA_DIR = DATA_DIR / "structural"
ERROR_DATA_DIR = DATA_DIR / "residual_error"


st.set_page_config(
    page_title="PharmaAI Model Reviewer",
    page_icon="📊",
    layout="wide",
)


def initialize_session_state() -> None:
    defaults = {
        "selected_absorption_model": None,
        "selected_structural_model": None,
        "selected_error_model": None,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_after_absorption_change() -> None:
    st.session_state["selected_structural_model"] = None
    st.session_state["selected_error_model"] = None


def reset_after_structural_change() -> None:
    st.session_state["selected_error_model"] = None


def create_candidate_from_folder(
    folder_name: str,
    model_folder: Path,
) -> CandidateModel:
    model_name = format_folder_name(folder_name)

    estimate_path = find_model_table(
        model_folder=model_folder,
        file_stem="estimates",
    )

    metric_path = find_model_table(
        model_folder=model_folder,
        file_stem="metrics",
    )

    gof_path = find_gof_image(model_folder)

    estimate_table = load_estimate_table(
        estimate_path
    )

    metric_table = load_metric_table(
        metric_path
    )

    validated_estimates = validate_estimate_table(
        estimate_table=estimate_table,
        model_name=model_name,
    )

    validated_metrics = validate_metric_table(
        metric_table=metric_table,
        model_name=model_name,
    )

    return CandidateModel(
        name=model_name,
        estimates=validated_estimates,
        metrics=validated_metrics,
        folder=model_folder,
        gof_path=gof_path,
    )


def display_two_model_gof_comparison(
    reference_model: CandidateModel,
    candidate_model: CandidateModel,
) -> None:
    st.subheader("4. GOF Comparison")

    reference_column, candidate_column = st.columns(2)

    with reference_column:
        st.markdown(
            f"#### {reference_model.name}"
        )

        if reference_model.gof_path is None:
            st.warning(
                "GOF image not found.\n\n"
                f"Save `gof.png` inside:\n\n"
                f"`{reference_model.folder}`"
            )
        else:
            st.image(
                str(reference_model.gof_path),
                caption=(
                    f"{reference_model.name} combined GOF plots"
                ),
                use_container_width=True,
            )

    with candidate_column:
        st.markdown(
            f"#### {candidate_model.name}"
        )

        if candidate_model.gof_path is None:
            st.warning(
                "GOF image not found.\n\n"
                f"Save `gof.png` inside:\n\n"
                f"`{candidate_model.folder}`"
            )
        else:
            st.image(
                str(candidate_model.gof_path),
                caption=(
                    f"{candidate_model.name} combined GOF plots"
                ),
                use_container_width=True,
            )

    st.caption(
        "Each image should contain the complete four-panel "
        "goodness-of-fit figure."
    )


def display_two_model_results(
    reference_model: CandidateModel,
    candidate_model: CandidateModel,
) -> None:
    candidates = [
        reference_model,
        candidate_model,
    ]

    parameter_comparison = compare_estimates(
        candidates
    )

    metric_comparison = compare_metrics(
        candidates
    )

    metric_differences = calculate_metric_differences(
        metric_comparison=metric_comparison,
        reference_model=reference_model.name,
        candidate_model=candidate_model.name,
        selected_metrics=[
            "OFV",
            "-2LL",
            "AIC",
            "BIC",
        ],
    )

    st.subheader(
        "1. Parameter Estimate Comparison"
    )

    st.dataframe(
        parameter_comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "An outer join is used. Parameters unique to one model "
        "are retained, and the other model shows a blank value."
    )

    st.subheader(
        "2. Complete Metric Comparison"
    )

    st.dataframe(
        metric_comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "An outer join is used. Model-specific metric rows, "
        "including different ETA-shrinkage rows, are retained."
    )

    st.subheader(
        "3. OFV, -2LL, AIC, and BIC Differences"
    )

    if metric_differences.empty:
        st.warning(
            "No matching numeric OFV, -2LL, AIC, or BIC rows "
            "were found in both models."
        )
    else:
        st.dataframe(
            metric_differences,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            f"Difference is {candidate_model.name} minus "
            f"{reference_model.name}. A negative value means "
            "the candidate has a lower metric value."
        )

    display_two_model_gof_comparison(
        reference_model=reference_model,
        candidate_model=candidate_model,
    )


def render_two_model_stage(
    stage_id: str,
    stage_folder: Path,
    selection_session_key: str,
    key_prefix: str,
    on_selection_change: Callable[[], None] | None = None,
    show_header: bool = True,
) -> None:
    stage = STAGE_DEFINITIONS[
        stage_id
    ]

    if show_header:
        st.header(
            stage.display_name
        )

    st.write(
        stage.description
    )

    available_models = discover_models(
        stage_folder
    )

    if len(available_models) < 2:
        st.warning(
            "At least two model folders are required in:\n\n"
            f"`{stage_folder}`\n\n"
            "Each model folder should contain:\n\n"
            "- `estimates.xlsx` or `estimates.csv`\n"
            "- `metrics.xlsx` or `metrics.csv`\n"
            "- `gof.png`"
        )
        return

    folder_names = list(
        available_models.keys()
    )

    reference_column, candidate_column = st.columns(
        2
    )

    with reference_column:
        reference_folder_name = st.selectbox(
            "Reference model",
            options=folder_names,
            format_func=format_folder_name,
            key=f"{key_prefix}_reference",
        )

    candidate_options = [
        folder_name
        for folder_name in folder_names
        if folder_name != reference_folder_name
    ]

    with candidate_column:
        candidate_folder_name = st.selectbox(
            "Candidate model",
            options=candidate_options,
            format_func=format_folder_name,
            key=f"{key_prefix}_candidate",
        )

    try:
        reference_model = create_candidate_from_folder(
            folder_name=reference_folder_name,
            model_folder=available_models[
                reference_folder_name
            ],
        )

        candidate_model = create_candidate_from_folder(
            folder_name=candidate_folder_name,
            model_folder=available_models[
                candidate_folder_name
            ],
        )

        st.success(
            "Model files loaded successfully."
        )

        display_two_model_results(
            reference_model=reference_model,
            candidate_model=candidate_model,
        )

    except (
        ValueError,
        TypeError,
        FileNotFoundError,
        pd.errors.ParserError,
    ) as error:
        st.error(
            str(error)
        )
        return

    st.subheader(
        "5. Model Selection"
    )

    selected_model = st.radio(
        "Select the preferred model",
        options=[
            reference_model.name,
            candidate_model.name,
        ],
        key=f"{key_prefix}_preferred_model",
        horizontal=True,
    )

    if st.button(
        "Confirm Model Selection",
        key=f"{key_prefix}_confirm",
        type="primary",
    ):
        previous_selection = st.session_state.get(
            selection_session_key
        )

        if (
            previous_selection != selected_model
            and on_selection_change is not None
        ):
            on_selection_change()

        st.session_state[
            selection_session_key
        ] = selected_model

        st.success(
            f"Selected model: {selected_model}"
        )

    current_selection = st.session_state.get(
        selection_session_key
    )

    if current_selection:
        st.info(
            "Current confirmed selection: "
            f"**{current_selection}**"
        )


def render_absorption_stage() -> None:
    st.header(
        "Stage 1: Absorption Model Selection"
    )

    workflow_choice = st.radio(
        "Do you need to compare absorption models?",
        options=[
            "Yes, compare absorption models",
            "No, use a fixed absorption model",
        ],
        key="absorption_workflow_choice",
    )

    if (
        workflow_choice
        == "No, use a fixed absorption model"
    ):
        fixed_absorption = st.text_input(
            "Fixed absorption model",
            placeholder="Example: FIRST ORDER",
            key="fixed_absorption_model",
        )

        if st.button(
            "Confirm Fixed Absorption Model",
            key="confirm_fixed_absorption",
            type="primary",
        ):
            fixed_absorption = (
                fixed_absorption.strip()
            )

            if not fixed_absorption:
                st.error(
                    "Enter the fixed absorption model."
                )
                return

            previous_selection = st.session_state.get(
                "selected_absorption_model"
            )

            if previous_selection != fixed_absorption:
                reset_after_absorption_change()

            st.session_state[
                "selected_absorption_model"
            ] = fixed_absorption

            st.success(
                "Fixed absorption model selected: "
                f"{fixed_absorption}"
            )

        current_absorption = st.session_state.get(
            "selected_absorption_model"
        )

        if current_absorption:
            st.info(
                "Current confirmed absorption model: "
                f"**{current_absorption}**"
            )

        return

    render_two_model_stage(
        stage_id=ABSORPTION_STAGE,
        stage_folder=ABSORPTION_DATA_DIR,
        selection_session_key=(
            "selected_absorption_model"
        ),
        key_prefix="absorption",
        on_selection_change=(
            reset_after_absorption_change
        ),
        show_header=False,
    )


def render_structural_stage() -> None:
    st.header(
        "Stage 2: Structural Model Selection"
    )

    selected_absorption = st.session_state.get(
        "selected_absorption_model"
    )

    if selected_absorption is None:
        st.info(
            "Complete Stage 1 before starting "
            "structural-model selection."
        )
        return

    st.info(
        "Absorption model carried forward: "
        f"**{selected_absorption}**"
    )

    st.write(
        "Both structural candidates should use the selected "
        "absorption model shown above."
    )

    render_two_model_stage(
        stage_id=STRUCTURAL_STAGE,
        stage_folder=STRUCTURAL_DATA_DIR,
        selection_session_key=(
            "selected_structural_model"
        ),
        key_prefix="structural",
        on_selection_change=(
            reset_after_structural_change
        ),
        show_header=False,
    )


def render_error_stage() -> None:
    """
    Compare all available residual-error models together.

    Typical folders:
        additive
        proportional
        combined
    """

    st.header(
        "Stage 3: Residual Error Model Selection"
    )

    selected_absorption = st.session_state.get(
        "selected_absorption_model"
    )

    selected_structural = st.session_state.get(
        "selected_structural_model"
    )

    if selected_structural is None:
        st.info(
            "Complete Stage 2 before starting "
            "residual-error-model selection."
        )
        return

    st.info(
        "Components carried forward:\n\n"
        f"- Absorption model: **{selected_absorption}**\n"
        f"- Structural model: **{selected_structural}**"
    )

    st.write(
        "All residual-error candidates should use the selected "
        "absorption and structural model."
    )

    available_models = discover_models(
        ERROR_DATA_DIR
    )

    if len(available_models) < 2:
        st.warning(
            "At least two residual-error model folders are required in:\n\n"
            f"`{ERROR_DATA_DIR}`\n\n"
            "For a complete comparison, create:\n\n"
            "- `additive/`\n"
            "- `proportional/`\n"
            "- `combined/`\n\n"
            "Each folder should contain:\n\n"
            "- `estimates.xlsx` or `estimates.csv`\n"
            "- `metrics.xlsx` or `metrics.csv`\n"
            "- `gof.png`"
        )
        return

    preferred_order = [
        "additive",
        "proportional",
        "combined",
    ]

    ordered_folder_names = [
        folder_name
        for folder_name in preferred_order
        if folder_name in available_models
    ]

    additional_folder_names = [
        folder_name
        for folder_name in available_models
        if folder_name not in preferred_order
    ]

    ordered_folder_names.extend(
        additional_folder_names
    )

    try:
        residual_candidates = [
            create_candidate_from_folder(
                folder_name=folder_name,
                model_folder=available_models[
                    folder_name
                ],
            )
            for folder_name in ordered_folder_names
        ]

        parameter_comparison = compare_estimates(
            residual_candidates
        )

        metric_comparison = compare_metrics(
            residual_candidates
        )

    except (
        ValueError,
        TypeError,
        FileNotFoundError,
        pd.errors.ParserError,
    ) as error:
        st.error(
            str(error)
        )
        return

    st.success(
        f"{len(residual_candidates)} residual-error "
        "model files loaded successfully."
    )

    st.subheader(
        "1. Parameter Estimate Comparison"
    )

    st.dataframe(
        parameter_comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "An outer join is used. Parameters unique to one "
        "residual-error model are retained."
    )

    st.subheader(
        "2. Complete Metric Comparison"
    )

    st.dataframe(
        metric_comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "All model-specific metric rows are retained."
    )

    st.subheader(
        "3. OFV, -2LL, AIC, and BIC Differences"
    )

    model_names = [
        candidate.name
        for candidate in residual_candidates
    ]

    reference_model_name = st.selectbox(
        "Reference residual-error model",
        options=model_names,
        key="residual_error_difference_reference",
    )

    difference_tables: list[
        pd.DataFrame
    ] = []

    for candidate_name in model_names:
        if candidate_name == reference_model_name:
            continue

        difference_table = calculate_metric_differences(
            metric_comparison=metric_comparison,
            reference_model=reference_model_name,
            candidate_model=candidate_name,
            selected_metrics=[
                "OFV",
                "-2LL",
                "AIC",
                "BIC",
            ],
        )

        if not difference_table.empty:
            difference_tables.append(
                difference_table
            )

    if not difference_tables:
        st.warning(
            "No matching numeric OFV, -2LL, AIC, or BIC "
            "rows were found."
        )
    else:
        for difference_table in difference_tables:
            st.dataframe(
                difference_table,
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "Each difference is candidate minus reference. "
            "A negative value means the candidate has a lower metric."
        )

    st.subheader(
        "4. GOF Comparison"
    )

    gof_columns = st.columns(
        len(residual_candidates)
    )

    for column, candidate in zip(
        gof_columns,
        residual_candidates,
    ):
        with column:
            st.markdown(
                f"#### {candidate.name}"
            )

            if candidate.gof_path is None:
                st.warning(
                    "GOF image not found.\n\n"
                    f"Save `gof.png` inside:\n\n"
                    f"`{candidate.folder}`"
                )
            else:
                st.image(
                    str(candidate.gof_path),
                    caption=(
                        f"{candidate.name} combined GOF plots"
                    ),
                    use_container_width=True,
                )

    st.caption(
        "Each GOF image should contain the complete "
        "four-panel goodness-of-fit figure."
    )

    st.subheader(
        "5. Residual Error Model Selection"
    )

    selected_model = st.radio(
        "Select the preferred residual-error model",
        options=model_names,
        key="residual_error_preferred_model",
        horizontal=True,
    )

    if st.button(
        "Confirm Residual Error Model",
        key="residual_error_confirm",
        type="primary",
    ):
        st.session_state[
            "selected_error_model"
        ] = selected_model

        st.success(
            "Selected residual-error model: "
            f"{selected_model}"
        )

    current_selection = st.session_state.get(
        "selected_error_model"
    )

    if current_selection:
        st.info(
            "Current confirmed residual-error model: "
            f"**{current_selection}**"
        )


def render_sidebar_summary() -> None:
    st.sidebar.header(
        "Current Model Selection"
    )

    selected_absorption = st.session_state.get(
        "selected_absorption_model"
    )

    selected_structural = st.session_state.get(
        "selected_structural_model"
    )

    selected_error = st.session_state.get(
        "selected_error_model"
    )

    st.sidebar.markdown(
        "**Absorption model**"
    )

    st.sidebar.write(
        selected_absorption
        or "Not selected"
    )

    st.sidebar.markdown(
        "**Structural model**"
    )

    st.sidebar.write(
        selected_structural
        or "Not selected"
    )

    st.sidebar.markdown(
        "**Residual error model**"
    )

    st.sidebar.write(
        selected_error
        or "Not selected"
    )

    if (
        selected_absorption
        and selected_structural
        and selected_error
    ):
        final_summary = create_final_model_summary(
            absorption_model=selected_absorption,
            structural_model=selected_structural,
            residual_error_model=selected_error,
        )

        st.sidebar.success(
            "Final base model complete"
        )

        st.sidebar.json(
            final_summary
        )


def main() -> None:
    initialize_session_state()

    st.title(
        "PharmaAI Model Reviewer"
    )

    st.write(
        "Sequential comparison of absorption, structural, "
        "and residual-error models."
    )

    st.markdown(
        """
        **Workflow**

        1. Compare absorption models or specify a fixed absorption model.
        2. Compare structural models.
        3. Compare all available residual-error models.
        4. Review the final selected base model.
        """
    )

    render_absorption_stage()

    st.divider()

    render_structural_stage()

    st.divider()

    render_error_stage()

    render_sidebar_summary()


if __name__ == "__main__":
    main()