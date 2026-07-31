from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class CandidateModel:
    """
    Represents one candidate model in a model-selection comparison.

    Candidate names are not hard-coded. Examples include:

    - ZERO ORDER
    - FIRST ORDER
    - ONE COMP
    - TWO COMP
    - MICHAELIS MENTEN
    - ADDITIVE
    - PROPORTIONAL
    - COMBINED
    """

    name: str
    estimates: pd.DataFrame
    metrics: pd.DataFrame
    folder: Path | None = None
    gof_path: Path | None = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "Candidate model name cannot be empty."
            )