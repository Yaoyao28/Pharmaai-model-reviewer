from __future__ import annotations

import os


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
).strip().lower()

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434",
).strip()

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b",
).strip()

OLLAMA_TEMPERATURE = float(
    os.getenv(
        "OLLAMA_TEMPERATURE",
        "0.2",
    )
)
