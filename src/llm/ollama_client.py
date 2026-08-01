from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import ollama

from src.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
)
from src.llm.base import LLMClient
from src.prompts import (
    PHARMACOMETRIC_REVIEW_SYSTEM_PROMPT,
    get_task_prompt,
)


class OllamaClient(LLMClient):
    """Local, no-API-key Ollama implementation."""

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        host: str = OLLAMA_HOST,
    ) -> None:
        self._model = model
        self._host = host
        self._client = ollama.Client(host=host)

    @property
    def provider_name(self) -> str:
        return "Ollama"

    @property
    def model_name(self) -> str:
        return self._model

    def check_connection(self) -> tuple[bool, str]:
        try:
            response = self._client.list()
        except Exception as error:
            return (
                False,
                f"Could not connect to Ollama at "
                f"{self._host}: {error}",
            )

        installed_names: set[str] = set()

        models = getattr(response, "models", None)

        if models is None and isinstance(response, dict):
            models = response.get("models", [])

        for item in models or []:
            name = getattr(item, "model", None)

            if name is None and isinstance(item, dict):
                name = item.get("model") or item.get("name")

            if name:
                installed_names.add(str(name))

        if (
            installed_names
            and self._model not in installed_names
        ):
            return (
                False,
                f"Ollama is running, but '{self._model}' is "
                "not installed. Run: "
                f"ollama pull {self._model}",
            )

        return (
            True,
            f"Connected to Ollama at {self._host}. "
            f"Model: {self._model}.",
        )

    def generate_review(
        self,
        evidence: Mapping[str, Any],
    ) -> str:
        review_type = str(
            evidence.get("review_type", "")
        ).strip()

        if not review_type:
            raise ValueError(
                "Evidence must contain review_type."
            )

        task_prompt = get_task_prompt(review_type)

        evidence_json = json.dumps(
            evidence,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            PHARMACOMETRIC_REVIEW_SYSTEM_PROMPT
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"{task_prompt}\n\n"
                            "Structured application-generated "
                            f"evidence:\n\n{evidence_json}\n\n"
                            "Generate the review now."
                        ),
                    },
                ],
                options={
                    "temperature": OLLAMA_TEMPERATURE,
                },
            )
        except Exception as error:
            raise RuntimeError(
                "Ollama review generation failed. Confirm "
                "that Ollama is running and that the model "
                f"'{self._model}' is installed. Details: "
                f"{error}"
            ) from error

        message = getattr(response, "message", None)
        content = getattr(message, "content", None)

        if content is None and isinstance(response, dict):
            content = (
                response.get("message", {})
                .get("content", "")
            )

        review = str(content or "").strip()

        if not review:
            raise RuntimeError(
                "Ollama returned an empty review."
            )

        return review
