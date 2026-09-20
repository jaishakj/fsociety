from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.modules.reality.domains.models import Domain  # noqa: F401 - required for relationship resolution
from app.modules.reality.sources.models import Source  # noqa: F401 - required for relationship resolution


class Difficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EvidenceLevel(str, enum.Enum):
    WELL_ESTABLISHED = "well_established"
    SUPPORTED = "supported"
    MIXED = "mixed"
    SPECULATIVE = "speculative"
    NOT_APPLICABLE = "not_applicable"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    RESEARCH = "research"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class RelationType(str, enum.Enum):
    RELATED = "related"
    PREREQUISITE = "prerequisite"
    CONTRASTS_WITH = "contrasts_with"
    EXTENDS = "extends"
    EXAMPLE_OF = "example_of"
    CAUSES = "causes"
    INFLUENCES = "influences"
    PART_OF = "part_of"


class Concept(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reality_concepts"

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)

    domain_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_domains.id"), index=True
    )
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(
            Difficulty,
            name="reality_difficulty",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=Difficulty.BEGINNER
    )
    estimated_reading_minutes: Mapped[int] = mapped_column(Integer, default=8)

    # {"sections": [{"type": "definition", "title": "...", "content": "..."}, ...]}
    content: Mapped[dict] = mapped_column(JSONB, default=dict)

    evidence_level: Mapped[EvidenceLevel] = mapped_column(
        Enum(
            EvidenceLevel,
            name="reality_evidence_level",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        )
    )
    status: Mapped[ContentStatus] = mapped_column(
        Enum(
            ContentStatus,
            name="reality_content_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=ContentStatus.DRAFT,
        index=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    domain: Mapped["Domain"] = relationship(back_populates="concepts")

    tags: Mapped[list["ConceptTag"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )
    sources: Mapped[list["ConceptSource"]] = relationship(
        back_populates="concept", cascade="all, delete-orphan"
    )

    outgoing_relations: Mapped[list["ConceptRelation"]] = relationship(
        back_populates="from_concept",
        foreign_keys="ConceptRelation.from_concept_id",
        cascade="all, delete-orphan",
    )


class Tag(UUIDMixin, Base):
    __tablename__ = "reality_tags"

    name: Mapped[str] = mapped_column(String(100), unique=True)


class ConceptTag(Base):
    __tablename__ = "reality_concept_tags"

    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_concepts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_tags.id", ondelete="CASCADE"), primary_key=True
    )

    concept: Mapped["Concept"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship()


class ConceptSource(Base):
    """Links a concept (optionally one section within it) to a Source."""

    __tablename__ = "reality_concept_sources"

    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_concepts.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_sources.id", ondelete="CASCADE"), primary_key=True
    )
    # Which content section this source backs, e.g. "evidence", "limitations".
    # Null means it supports the concept generally (e.g. "further reading").
    section_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    concept: Mapped["Concept"] = relationship(back_populates="sources")
    source: Mapped["Source"] = relationship()


class ConceptRelation(UUIDMixin, Base):
    __tablename__ = "reality_concept_relations"
    __table_args__ = (
        UniqueConstraint(
            "from_concept_id", "to_concept_id", "relation_type", name="uq_reality_concept_relation"
        ),
    )

    from_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_concepts.id", ondelete="CASCADE"), index=True
    )
    to_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("reality_concepts.id", ondelete="CASCADE"), index=True
    )
    relation_type: Mapped[RelationType] = mapped_column(
        Enum(
            RelationType,
            name="reality_relation_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        )
    )

    from_concept: Mapped["Concept"] = relationship(
        back_populates="outgoing_relations", foreign_keys=[from_concept_id]
    )
    to_concept: Mapped["Concept"] = relationship(foreign_keys=[to_concept_id])
