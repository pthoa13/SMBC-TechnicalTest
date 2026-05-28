import pytest

from brightlearn_site.translation.exceptions import InvalidLLMResponseError
from brightlearn_site.translation.json_repair import repair_json
from brightlearn_site.translation.response_parser import parse_translation_json


def test_parse_translation_json_accepts_wrapped_response() -> None:
    bundle = parse_translation_json(
        '{"translations":{"es":"Hola","fr":"Bonjour","de":"Hallo"}}'
    )

    assert bundle.es == "Hola"


def test_parse_translation_json_rejects_unwrapped_response() -> None:
    with pytest.raises(InvalidLLMResponseError):
        parse_translation_json('{"es":"Hola","fr":"Bonjour","de":"Hallo"}')


def test_parse_translation_json_rejects_missing_language_key() -> None:
    with pytest.raises(InvalidLLMResponseError):
        parse_translation_json('{"translations":{"es":"Hola","fr":"Bonjour"}}')


def test_parse_translation_json_rejects_extra_language_key() -> None:
    with pytest.raises(InvalidLLMResponseError):
        parse_translation_json(
            '{"translations":{"es":"Hola","fr":"Bonjour","de":"Hallo","it":"Ciao"}}'
        )


def test_repair_json_extracts_object_from_extra_prose() -> None:
    repaired = repair_json(
        'Here is the JSON: {"translations":{"es":"Hola","fr":"Bonjour","de":"Hallo"}} Thanks.'
    )

    bundle = parse_translation_json(repaired)

    assert bundle.de == "Hallo"
