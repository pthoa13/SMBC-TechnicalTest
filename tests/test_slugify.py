from brightlearn_site.slugify import slugify, slugify_file_stem, unique_slug


def test_slugify_creates_windows_safe_slug() -> None:
    assert slugify("CON") == "con-item"
    assert slugify("The Big Toe: A Guide!") == "the-big-toe-a-guide"


def test_unique_slug_adds_stable_suffix() -> None:
    used: set[str] = set()

    assert unique_slug("Duplicate Title", used) == "duplicate-title"
    assert unique_slug("Duplicate Title", used) == "duplicate-title-2"
    assert unique_slug("Duplicate Title", used) == "duplicate-title-3"


def test_slugify_file_stem_preserves_underscores() -> None:
    assert slugify_file_stem("brightlearn_books") == "brightlearn_books"
    assert slugify_file_stem("brightlearn_books (2)") == "brightlearn_books-2"
