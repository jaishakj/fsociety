from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.reality.concepts.models import (
    Concept,
    ConceptRelation,
    ConceptSource,
    ConceptTag,
    ContentStatus,
    Difficulty,
    Tag,
)
from app.modules.reality.domains.models import Domain

_EAGER = (
    selectinload(Concept.domain),
    selectinload(Concept.tags).selectinload(ConceptTag.tag),
    selectinload(Concept.sources).selectinload(ConceptSource.source),
)


def get_concept_by_slug(db: Session, slug: str) -> Concept | None:
    stmt = select(Concept).options(*_EAGER).where(Concept.slug == slug)
    return db.scalar(stmt)


def get_concept_by_id(db: Session, concept_id: UUID) -> Concept | None:
    stmt = select(Concept).options(*_EAGER).where(Concept.id == concept_id)
    return db.scalar(stmt)


def list_concepts(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    domain_slug: str | None = None,
    difficulty: Difficulty | None = None,
    search: str | None = None,
    status: ContentStatus | None = ContentStatus.PUBLISHED,
) -> tuple[list[Concept], int]:
    stmt = select(Concept).options(
        selectinload(Concept.domain), selectinload(Concept.tags).selectinload(ConceptTag.tag)
    )

    if status is not None:
        stmt = stmt.where(Concept.status == status)
    if domain_slug:
        stmt = stmt.join(Domain).where(Domain.slug == domain_slug)
    if difficulty is not None:
        stmt = stmt.where(Concept.difficulty == difficulty)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Concept.title.ilike(like),
                Concept.summary.ilike(like),
                Concept.id.in_(
                    select(ConceptTag.concept_id).join(Tag).where(Tag.name.ilike(like))
                ),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Concept.title.asc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt))
    return items, total


def get_related_concepts(db: Session, concept_id: UUID) -> list[tuple[str, Concept]]:
    stmt = (
        select(ConceptRelation)
        .options(
            selectinload(ConceptRelation.to_concept).selectinload(Concept.domain),
        )
        .where(ConceptRelation.from_concept_id == concept_id)
    )
    relations = db.scalars(stmt)
    return [(relation.relation_type.value, relation.to_concept) for relation in relations]


def get_tag_by_name(db: Session, name: str) -> Tag | None:
    return db.scalar(select(Tag).where(Tag.name == name))
