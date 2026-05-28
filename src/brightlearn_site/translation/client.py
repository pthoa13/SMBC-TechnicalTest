"""Low-level OpenAI-compatible LLM client."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from brightlearn_site.translation.exceptions import (
    LLMConfigurationError,
    LLMNonRetryableError,
    LLMRateLimitError,
    LLMTransientError,
)
from brightlearn_site.translation.prompts import TRANSLATION_SYSTEM_PROMPT


@dataclass(frozen=True)
class LLMClientConfig:
    provider: str
    api_key: str
    model: str
    base_url: str
    timeout_seconds: int


class OpenAICompatibleTranslationClient:
    def __init__(self, config: LLMClientConfig) -> None:
        self.config = config

    def translate_summary(self, user_prompt: str) -> str:
        if not self.config.api_key:
            raise LLMConfigurationError("LLM_API_KEY is not configured.")

        try:
            response = httpx.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": TRANSLATION_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
                timeout=self.config.timeout_seconds,
            )
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as error:
            message = "LLM request failed due to a transient network error."
            raise LLMTransientError(message) from error

        if response.status_code == 429:
            raise LLMRateLimitError("LLM provider rate limit exceeded.")

        if 500 <= response.status_code <= 599:
            raise LLMTransientError(f"LLM provider returned {response.status_code}.")

        if response.status_code >= 400:
            raise LLMNonRetryableError(f"LLM provider returned {response.status_code}.")

        try:
            payload = response.json()
        except ValueError as error:
            raise LLMNonRetryableError("LLM response body was not valid JSON.") from error

        try:
            return str(payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as error:
            raise LLMNonRetryableError("LLM response did not include message content.") from error
