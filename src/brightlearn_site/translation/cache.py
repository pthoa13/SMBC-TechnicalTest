"""Translation cache utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import ValidationError

from brightlearn_site.models import TranslationBundle
from brightlearn_site.translation.exceptions import TranslationCacheError

TARGET_LANGUAGES = ("es", "fr", "de")
SOURCE_LANGUAGE = "en"
PROMPT_VERSION = "summary-translation-v1"


def build_translation_cache_key(
    *,
    provider: str,
    model: str,
    book_title: str,
    description: str,
    source_language: str = SOURCE_LANGUAGE,
    target_languages: tuple[str, ...] = TARGET_LANGUAGES,
    prompt_version: str = PROMPT_VERSION,
) -> str:
    payload = {
        "provider": provider,
        "model": model,
        "source_language": source_language,
        "target_languages": list(target_languages),
        "book_title": book_title,
        "description_hash": hashlib.sha256(description.encode("utf-8")).hexdigest(),
        "prompt_version": prompt_version,
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class TranslationCache:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._entries = self._load()

    def get(self, key: str) -> TranslationBundle | None:
        payload = self._entries.get(key)
        if payload is None:
            return None
        try:
            return TranslationBundle.model_validate(payload)
        except ValidationError:
            return None

    def set(self, key: str, value: TranslationBundle) -> None:
        self._entries[key] = value.model_dump()
        self._save()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            message = f"Translation cache is not valid JSON: {self.path}"
            raise TranslationCacheError(message) from error
        except OSError as error:
            raise TranslationCacheError(f"Could not read translation cache: {self.path}") from error

        if not isinstance(payload, dict):
            raise TranslationCacheError("Translation cache root must be a JSON object.")

        return payload

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._entries, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except OSError as error:
            message = f"Could not write translation cache: {self.path}"
            raise TranslationCacheError(message) from error
