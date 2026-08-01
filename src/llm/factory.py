from __future__ import annotations

from src.config import LLM_PROVIDER
from src.llm.base import LLMClient


def create_llm_client(
    provider: str | None = None,
) -> LLMClient:
    """
    Create the configured LLM client.

    Add future providers here without changing the evidence pipeline
    or Streamlit review workflow.
    """

    selected_provider = (
        provider or LLM_PROVIDER
    ).strip().lower()

    if selected_provider == "ollama":
        from src.llm.ollama_client import OllamaClient

        return OllamaClient()

    # Future examples:
    # if selected_provider == "openai":
    #     from src.llm.openai_client import OpenAIClient
    #     return OpenAIClient()
    #
    # if selected_provider == "anthropic":
    #     from src.llm.anthropic_client import AnthropicClient
    #     return AnthropicClient()
    #
    # if selected_provider == "gemini":
    #     from src.llm.gemini_client import GeminiClient
    #     return GeminiClient()

    raise ValueError(
        f"Unsupported LLM provider: {selected_provider}"
    )
