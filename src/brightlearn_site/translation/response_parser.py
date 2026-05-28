"""Parse and validate translation responses."""

from __future__ import annotations

import json

from pydantic import ValidationError

from brightlearn_site.models import TranslationBundle
from brightlearn_site.translation.exceptions import InvalidLLMResponseError


def parse_translation_json(raw: str) -> TranslationBundle:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise InvalidLLMResponseError(f"Translation response is not valid JSON: {error}") from error

    if not isinstance(payload, dict) or set(payload.keys()) != {"translations"}:
        raise InvalidLLMResponseError(
            "Translation response must be a JSON object with only a 'translations' key."
        )

    translations = payload["translations"]
    if not isinstance(translations, dict):
        raise InvalidLLMResponseError("'translations' must be a JSON object.")

    if set(translations.keys()) != {"es", "fr", "de"}:
        raise InvalidLLMResponseError("Translations must contain exactly 'es', 'fr', and 'de'.")

    try:
        return TranslationBundle.model_validate(translations)
    except ValidationError as error:
        raise InvalidLLMResponseError(f"Translation payload failed validation: {error}") from error
