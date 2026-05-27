"""Parse and validate translation responses."""

from __future__ import annotations

import json

from brightlearn_site.models import TranslationBundle


def parse_translation_json(raw: str) -> TranslationBundle:
    payload = json.loads(raw)
    translations = payload.get("translations", payload)
    return TranslationBundle.model_validate(translations)
