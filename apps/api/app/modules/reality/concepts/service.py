import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.modules.reality.concepts import repository
from app.modules.reality.concepts.models import (
    Concept,
    ConceptSource,
    ConceptTag,
    ContentStatus,
    Difficulty,
    EvidenceLevel,
    Tag,
)
from app.modules.reality.concepts.schemas import ConceptCreate
from app.modules.reality.domains import repository as domain_repository


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = repository.get_tag_by_name(db, name)
    if tag:
        return tag
    tag = Tag(name=name)
    db.add(tag)
    db.flush()
    return tag


def create_concept(db: Session, data: ConceptCreate) -> Concept:
    domain = domain_repository.get_domain_by_slug(db, data.domain_slug)
    if not domain:
        raise ValueError(f"unknown domain_slug '{data.domain_slug}'")

    status = ContentStatus(data.status)
    concept = Concept(
        slug=data.slug or slugify(data.title),
        title=data.title,
        summary=data.summary,
        domain_id=domain.id,
        difficulty=Difficulty(data.difficulty),
        evidence_level=EvidenceLevel(data.evidence_level),
        estimated_reading_minutes=data.estimated_reading_minutes,
        content={"sections": [section.model_dump() for section in data.sections]},
        status=status,
        published_at=datetime.now(timezone.utc) if status == ContentStatus.PUBLISHED else None,
    )

    for name in data.tags:
        tag = get_or_create_tag(db, name)
        concept.tags.append(ConceptTag(tag=tag))

    for source_id in data.source_ids:
        concept.sources.append(ConceptSource(source_id=source_id))

    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept


def concept_to_summary_dict(concept: Concept) -> dict:
    return {
        "id": concept.id,
        "slug": concept.slug,
        "title": concept.title,
        "summary": concept.summary,
        "difficulty": concept.difficulty.value,
        "evidence_level": concept.evidence_level.value,
        "estimated_reading_minutes": concept.estimated_reading_minutes,
        "domain": concept.domain,
    }


def concept_to_out_dict(concept: Concept) -> dict:
    return {
        "id": concept.id,
        "slug": concept.slug,
        "title": concept.title,
        "summary": concept.summary,
        "domain": concept.domain,
        "difficulty": concept.difficulty.value,
        "evidence_level": concept.evidence_level.value,
        "estimated_reading_minutes": concept.estimated_reading_minutes,
        "status": concept.status.value,
        "sections": concept.content.get("sections", []),
        "tags": [concept_tag.tag.name for concept_tag in concept.tags],
        "sources": [
            {"section_type": concept_source.section_type, "source": concept_source.source}
            for concept_source in concept.sources
        ],
    }
