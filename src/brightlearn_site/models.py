"""Internal data models for BrightLearn book content."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class Author(BaseModel):
    name: str
    profile_url: HttpUrl | None = None


class Section(BaseModel):
    title: str
    url: HttpUrl


class Chapter(BaseModel):
    chapter_number: int
    chapter_title: str
    sections: list[Section] = Field(default_factory=list)


class Book(BaseModel):
    book_title: str
    cover_image_url: HttpUrl
    author: Author
    book_id: str | None = None
    description: str
    table_of_contents: list[Chapter] = Field(default_factory=list)


class BookDataset(BaseModel):
    source: str | None = None
    extraction_date: str | None = None
    total_books: int | None = None
    books: list[Book] = Field(default_factory=list)


class TranslationBundle(BaseModel):
    es: str
    fr: str
    de: str
