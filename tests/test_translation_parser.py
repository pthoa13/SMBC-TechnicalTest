from brightlearn_site.translation.response_parser import parse_translation_json


def test_parse_translation_json_accepts_wrapped_response() -> None:
    bundle = parse_translation_json(
        '{"translations":{"es":"Hola","fr":"Bonjour","de":"Hallo"}}'
    )

    assert bundle.es == "Hola"
