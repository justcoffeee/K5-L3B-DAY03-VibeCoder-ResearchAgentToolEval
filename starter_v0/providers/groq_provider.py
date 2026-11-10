from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq's OpenAI-compatible endpoint, using a dedicated credential."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            default_model=os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b",
        )
