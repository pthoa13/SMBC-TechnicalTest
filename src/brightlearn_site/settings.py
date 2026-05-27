"""Application settings loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    translation_timeout_seconds: int = 60
    translation_max_retries: int = 5
    translation_cache_path: Path = Path("rendered/.cache/translations.json")


def load_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        translation_timeout_seconds=int(os.getenv("TRANSLATION_TIMEOUT_SECONDS", "60")),
        translation_max_retries=int(os.getenv("TRANSLATION_MAX_RETRIES", "5")),
        translation_cache_path=Path(
            os.getenv("TRANSLATION_CACHE_PATH", "rendered/.cache/translations.json")
        ),
    )
