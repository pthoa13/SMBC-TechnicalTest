from pathlib import Path

from pydantic import HttpUrl

from brightlearn_site.models import Author, Book, TranslationBundle
from brightlearn_site.settings import Settings
from brightlearn_site.translation.cache import TranslationCache, build_translation_cache_key
from brightlearn_site.translation.exceptions import LLMRateLimitError
from brightlearn_site.translation.retry import RetryPolicy
from brightlearn_site.translation.service import SummaryTranslationService


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def translate_summary(self, user_prompt: str) -> str:
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _settings(cache_path: Path) -> Settings:
    return Settings(
        llm_provider="openai",
        llm_api_key="test-key",
        llm_model="test-model",
        translation_cache_path=cache_path,
        translation_max_retries=2,
    )


def _book(description: str = "Original summary") -> Book:
    return Book(
        book_title="Sample Book",
        cover_image_url=HttpUrl("https://example.com/cover.png"),
        author=Author(name="Author"),
        description=description,
        table_of_contents=[],
    )


def test_service_uses_cache_before_client(tmp_path: Path) -> None:
    settings = _settings(tmp_path / "translations.json")
    cache = TranslationCache(settings.translation_cache_path)
    book = _book()
    key = build_translation_cache_key(
        provider=settings.llm_provider,
        model=settings.llm_model,
        book_title=book.book_title,
        description=book.description,
    )
    cache.set(key, TranslationBundle(es="ES", fr="FR", de="DE"))
    client = FakeClient([])
    service = SummaryTranslationService(settings=settings, cache=cache, client=client, sleep=False)

    result = service.translate_book(book)

    assert client.calls == 0
    assert result.es == "ES"
    assert result.used_fallback is False


def test_service_logs_cache_hit_and_miss(tmp_path: Path, caplog) -> None:
    settings = _settings(tmp_path / "translations.json")
    client = FakeClient(['{"translations":{"es":"ES","fr":"FR","de":"DE"}}'])
    service = SummaryTranslationService(settings=settings, client=client, sleep=False)

    with caplog.at_level("INFO"):
        service.translate_book(_book())
        service.translate_book(_book())

    assert "Translation cache miss" in caplog.text
    assert "Translation request started" in caplog.text
    assert "Translation request succeeded" in caplog.text
    assert "Translation cache hit" in caplog.text
    assert client.calls == 1


def test_service_recovers_from_malformed_cache_file(tmp_path: Path) -> None:
    cache_path = tmp_path / "translations.json"
    cache_path.write_text("{bad json", encoding="utf-8")
    settings = _settings(cache_path)
    client = FakeClient(['{"translations":{"es":"ES","fr":"FR","de":"DE"}}'])
    service = SummaryTranslationService(settings=settings, client=client, sleep=False)

    result = service.translate_book(_book())

    assert result.es == "ES"
    assert client.calls == 1
    assert cache_path.exists()
    assert list(tmp_path.glob("translations.corrupt-invalid-json-*.json"))


def test_service_repairs_extra_prose_and_caches_result(tmp_path: Path) -> None:
    settings = _settings(tmp_path / "translations.json")
    client = FakeClient(
        [
            'Here: {"translations":{"es":"ES","fr":"FR","de":"DE"}}',
        ]
    )
    service = SummaryTranslationService(settings=settings, client=client, sleep=False)

    result = service.translate_book(_book())

    assert result.es == "ES"
    assert TranslationCache(settings.translation_cache_path).get(
        build_translation_cache_key(
            provider=settings.llm_provider,
            model=settings.llm_model,
            book_title="Sample Book",
            description="Original summary",
        )
    )


def test_service_retries_rate_limit_then_succeeds(tmp_path: Path) -> None:
    settings = _settings(tmp_path / "translations.json")
    client = FakeClient(
        [
            LLMRateLimitError("rate limited"),
            '{"translations":{"es":"ES","fr":"FR","de":"DE"}}',
        ]
    )
    service = SummaryTranslationService(
        settings=settings,
        client=client,
        retry_policy=RetryPolicy(max_retries=2, base_delay_seconds=0),
        sleep=False,
    )

    result = service.translate_book(_book())

    assert client.calls == 2
    assert result.fr == "FR"


def test_service_falls_back_to_english_after_exhausted_retries(tmp_path: Path) -> None:
    settings = _settings(tmp_path / "translations.json")
    client = FakeClient(
        [
            LLMRateLimitError("rate limited"),
            LLMRateLimitError("still limited"),
        ]
    )
    service = SummaryTranslationService(
        settings=settings,
        client=client,
        retry_policy=RetryPolicy(max_retries=1, base_delay_seconds=0),
        sleep=False,
    )

    result = service.translate_book(_book())

    assert result.en == "Original summary"
    assert result.used_fallback is True
    assert result.error
