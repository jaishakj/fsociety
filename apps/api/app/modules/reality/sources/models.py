from __future__ import annotations

import enum

from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class SourceType(str, enum.Enum):
    RESEARCH_PAPER = "research_paper"
    BOOK = "book"
    ACADEMIC_BOOK = "academic_book"
    GOVERNMENT_REPORT = "government_report"
    INSTITUTIONAL_REPORT = "institutional_report"
    REVIEW = "review"
    NEWS = "news"
    ESSAY = "essay"
    WEBSITE = "website"
    DOCUMENTARY = "documentary"
    DATASET = "dataset"


class Source(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reality_sources"

    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[list] = mapped_column(JSONB, default=list)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(
            SourceType,
            name="reality_source_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        )
    )
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
