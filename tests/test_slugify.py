from brightlearn_site.slugify import slugify


def test_slugify_creates_windows_safe_slug() -> None:
    assert slugify("CON") == "con-item"
    assert slugify("The Big Toe: A Guide!") == "the-big-toe-a-guide"
