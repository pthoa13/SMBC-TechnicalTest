"""Prompt templates for strict JSON translation responses."""

TRANSLATION_SYSTEM_PROMPT = """You translate book summaries.

Return only valid JSON. Do not include Markdown fences, commentary, or extra keys.
The JSON must have this exact shape:
{"translations":{"es":"...","fr":"...","de":"..."}}
"""


def build_translation_user_prompt(book_title: str, description: str) -> str:
    return (
        "Translate only the book summary below into Spanish, French, and German. "
        "Do not translate the title, chapter titles, section titles, or full book content.\n\n"
        f"Book title for context: {book_title}\n\n"
        f"English summary:\n{description}"
    )
