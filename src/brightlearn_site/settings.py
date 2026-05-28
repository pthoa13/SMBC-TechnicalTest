"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    translation_timeout_seconds: int = 60
    translation_max_retries: int = 5
    llm_max_completion_tokens: int = 4096
    translation_cache_path: Path = Path("rendered/.cache/translations.json")


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_api_key=_clean_api_key(os.getenv("LLM_API_KEY", "")),
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        translation_timeout_seconds=int(os.getenv("TRANSLATION_TIMEOUT_SECONDS", "60")),
        translation_max_retries=int(os.getenv("TRANSLATION_MAX_RETRIES", "5")),
        llm_max_completion_tokens=int(os.getenv("LLM_MAX_COMPLETION_TOKENS", "4096")),
        translation_cache_path=Path(
            os.getenv("TRANSLATION_CACHE_PATH", "rendered/.cache/translations.json")
        ),
    )


def _clean_api_key(value: str) -> str:
    stripped = value.strip()
    if stripped.lower() in {"", "your_api_key_here", "replace_me", "changeme"}:
        return ""
    return stripped
