"""Retry policy for transient LLM failures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 5
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0

    @property
    def max_attempts(self) -> int:
        return self.max_retries + 1

    def delay_for_retry(self, retry_number: int) -> float:
        delay = self.base_delay_seconds * (2 ** max(retry_number - 1, 0))
        return min(delay, self.max_delay_seconds)
