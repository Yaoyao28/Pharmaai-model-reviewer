from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class LLMClient(ABC):
    """Shared interface implemented by every LLM provider."""

    @abstractmethod
    def generate_review(
        self,
        evidence: Mapping[str, Any],
    ) -> str:
        """Generate a grounded pharmacometric review."""
        raise NotImplementedError

    @abstractmethod
    def check_connection(self) -> tuple[bool, str]:
        """Return provider availability and a human-readable message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Display name for the provider."""
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Display name for the selected model."""
        raise NotImplementedError
