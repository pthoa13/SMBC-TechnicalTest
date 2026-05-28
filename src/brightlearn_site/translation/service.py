"""High-level summary translation workflow."""

from __future__ import annotations

import logging
import time
from typing import Protocol

from brightlearn_site.models import Book, SummaryTranslations, TranslationBundle
from brightlearn_site.settings import Settings
from brightlearn_site.translation.cache import (
    TranslationCache,
    build_translation_cache_key,
)
from brightlearn_site.translation.client import (
    LLMClientConfig,
    OpenAICompatibleTranslationClient,
)
from brightlearn_site.translation.exceptions import (
    InvalidLLMResponseError,
    LLMConfigurationError,
    LLMNonRetryableError,
    LLMRateLimitError,
    LLMTransientError,
    TranslationCacheError,
)
from brightlearn_site.translation.json_repair import repair_json
from brightlearn_site.translation.prompts import build_translation_user_prompt
from brightlearn_site.translation.response_parser import parse_translation_json
from brightlearn_site.translation.retry import RetryPolicy

logger = logging.getLogger(__name__)


class TranslationClient(Protocol):
    def translate_summary(self, user_prompt: str) -> str:
        ...


class TranslationService(Protocol):
    def translate_book(self, book: Book) -> SummaryTranslations:
        ...


class SummaryTranslationService:
    def __init__(
        self,
        *,
        settings: Settings,
        cache: TranslationCache | None = None,
        client: TranslationClient | None = None,
        retry_policy: RetryPolicy | None = None,
        sleep: bool = True,
    ) -> None:
        self.settings = settings
        self.cache = cache or TranslationCache(settings.translation_cache_path)
        self.client = client or OpenAICompatibleTranslationClient(
            LLMClientConfig(
                provider=settings.llm_provider,
                api_key=settings.llm_api_key,
                model=settings.llm_model,
                base_url=settings.llm_base_url,
                timeout_seconds=settings.translation_timeout_seconds,
                max_completion_tokens=settings.llm_max_completion_tokens,
            )
        )
        self.retry_policy = retry_policy or RetryPolicy(
            max_retries=settings.translation_max_retries
        )
        self.sleep = sleep

    def translate_book(self, book: Book) -> SummaryTranslations:
        key = build_translation_cache_key(
            provider=self.settings.llm_provider,
            model=self.settings.llm_model,
            book_title=book.book_title,
            description=book.description,
        )

        cached = self.cache.get(key)
        if cached is not None:
            logger.info("Translation cache hit. book=%s", book.book_title)
            return _summary_from_bundle(book.description, cached)

        logger.info(
            "Translation cache miss. book=%s model=%s max_completion_tokens=%s",
            book.book_title,
            self.settings.llm_model,
            self.settings.llm_max_completion_tokens,
        )
        prompt = build_translation_user_prompt(book.book_title, book.description)
        last_error: Exception | None = None

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                logger.info(
                    "Translation request started. book=%s attempt=%s/%s",
                    book.book_title,
                    attempt,
                    self.retry_policy.max_attempts,
                )
                raw_response = self.client.translate_summary(prompt)
                bundle = _parse_with_repair(raw_response)
                self.cache.set(key, bundle)
                logger.info("Translation request succeeded. book=%s", book.book_title)
                return _summary_from_bundle(book.description, bundle)
            except (LLMRateLimitError, LLMTransientError, InvalidLLMResponseError) as error:
                last_error = error
                if attempt >= self.retry_policy.max_attempts:
                    break
                logger.warning(
                    "Translation request failed; retrying. book=%s attempt=%s/%s error=%s",
                    book.book_title,
                    attempt,
                    self.retry_policy.max_attempts,
                    error,
                )
                self._wait_before_retry(attempt)
            except (LLMConfigurationError, LLMNonRetryableError, TranslationCacheError) as error:
                last_error = error
                logger.warning(
                    "Translation request stopped without retry. book=%s error=%s",
                    book.book_title,
                    error,
                )
                break

        message = str(last_error) if last_error else "Unknown translation failure."
        logger.warning("Using English fallback for %s: %s", book.book_title, message)
        return SummaryTranslations(en=book.description, used_fallback=True, error=message)

    def _wait_before_retry(self, attempt: int) -> None:
        if self.sleep:
            time.sleep(self.retry_policy.delay_for_retry(attempt))


class EnglishOnlyTranslationService:
    def translate_book(self, book: Book) -> SummaryTranslations:
        logger.info("Translation skipped; using English summary. book=%s", book.book_title)
        return SummaryTranslations(en=book.description, used_fallback=True)


def _parse_with_repair(raw_response: str) -> TranslationBundle:
    try:
        return parse_translation_json(raw_response)
    except InvalidLLMResponseError:
        repaired = repair_json(raw_response)
        if repaired == raw_response:
            raise
        return parse_translation_json(repaired)


def _summary_from_bundle(
    original_description: str,
    bundle: TranslationBundle,
) -> SummaryTranslations:
    return SummaryTranslations(
        en=original_description,
        es=bundle.es,
        fr=bundle.fr,
        de=bundle.de,
        used_fallback=False,
    )
