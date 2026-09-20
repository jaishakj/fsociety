from __future__ import annotations

import typing

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if typing.TYPE_CHECKING:
    from app.modules.reality.concepts.models import Concept


class Domain(UUIDMixin, TimestampMixin, Base):
    """Knowledge domain / taxonomy entry. Browsed by users as a "Topic"."""

    __tablename__ = "reality_domains"

    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    concepts: Mapped[list["Concept"]] = relationship(back_populates="domain")
