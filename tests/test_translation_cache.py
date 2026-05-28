from pathlib import Path

import pytest

from brightlearn_site.models import TranslationBundle
from brightlearn_site.translation.cache import (
    TranslationCache,
    build_translation_cache_key,
)
from brightlearn_site.translation.exceptions import TranslationCacheError


def test_translation_cache_round_trip(tmp_path: Path) -> None:
    cache = TranslationCache(tmp_path / "translations.json")
    key = build_translation_cache_key(
        provider="openai",
        model="gpt-test",
        book_title="Sample",
        description="Original summary",
    )

    cache.set(key, TranslationBundle(es="ES", fr="FR", de="DE"))

    reloaded = TranslationCache(tmp_path / "translations.json")
    bundle = reloaded.get(key)

    assert bundle is not None
    assert bundle.es == "ES"
    assert bundle.fr == "FR"
    assert bundle.de == "DE"


def test_translation_cache_key_changes_when_description_changes() -> None:
    base = {
        "provider": "openai",
        "model": "gpt-test",
        "book_title": "Sample",
    }

    first_key = build_translation_cache_key(description="Original summary", **base)
    second_key = build_translation_cache_key(description="Updated summary", **base)

    assert first_key != second_key


def test_translation_cache_key_includes_provider_and_model() -> None:
    first_key = build_translation_cache_key(
        provider="openai",
        model="gpt-test",
        book_title="Sample",
        description="Original summary",
    )
    second_key = build_translation_cache_key(
        provider="other-provider",
        model="gpt-test",
        book_title="Sample",
        description="Original summary",
    )
    third_key = build_translation_cache_key(
        provider="openai",
        model="other-model",
        book_title="Sample",
        description="Original summary",
    )

    assert first_key != second_key
    assert first_key != third_key


def test_translation_cache_rejects_malformed_cache_file(tmp_path: Path) -> None:
    cache_path = tmp_path / "translations.json"
    cache_path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(TranslationCacheError):
        TranslationCache(cache_path)
