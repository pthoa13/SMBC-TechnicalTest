from pathlib import Path


def test_language_switcher_javascript_targets_rendered_markup() -> None:
    script = Path("src/brightlearn_site/static/js/app.js").read_text(encoding="utf-8")
    template = Path("src/brightlearn_site/templates/book_index.html").read_text(encoding="utf-8")
    flags = Path("src/brightlearn_site/templates/partials/language_flags.html").read_text(
        encoding="utf-8"
    )

    assert "data-language" in script
    assert "data-summary-switcher" in script
    assert "data-summary-output" in script
    assert "data-summary-switcher" in template
    assert "data-summary-output" in template
    assert 'data-language="es"' in flags
    assert 'data-language="fr"' in flags
    assert 'data-language="de"' in flags
