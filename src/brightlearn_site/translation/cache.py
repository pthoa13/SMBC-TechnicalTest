"""Translation cache utilities."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from brightlearn_site.models import TranslationBundle
from brightlearn_site.translation.exceptions import TranslationCacheError

LOGGER = logging.getLogger(__name__)

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
            raw_cache = self.path.read_text(encoding="utf-8")
        except OSError as error:
            raise TranslationCacheError(f"Could not read translation cache: {self.path}") from error

        if not raw_cache.strip():
            self._quarantine_invalid_cache("empty")
            return {}

        try:
            payload = json.loads(raw_cache)
        except json.JSONDecodeError:
            self._quarantine_invalid_cache("invalid-json")
            return {}

        if not isinstance(payload, dict):
            self._quarantine_invalid_cache("invalid-root")
            return {}

        return payload

    def _quarantine_invalid_cache(self, reason: str) -> None:
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        quarantine_path = self.path.with_name(
            f"{self.path.stem}.corrupt-{reason}-{timestamp}{self.path.suffix}"
        )
        try:
            self.path.rename(quarantine_path)
        except OSError as error:
            LOGGER.warning(
                "Translation cache is %s and could not be quarantined; it will be overwritten "
                "on the next successful cache write. path=%s error=%s",
                reason,
                self.path,
                error,
            )
            return

        LOGGER.warning(
            "Translation cache is %s; moved aside and starting with an empty cache. old=%s new=%s",
            reason,
            self.path,
            quarantine_path,
        )

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
