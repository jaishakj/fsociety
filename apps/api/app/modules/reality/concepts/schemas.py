from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.reality.domains.schemas import DomainOut
from app.modules.reality.sources.schemas import SourceOut


class ContentSection(BaseModel):
    type: str
    title: str
    content: str


class ConceptSummaryOut(BaseModel):
    """Slim shape used in listings and as related-concept references."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    summary: str
    difficulty: str
    evidence_level: str
    estimated_reading_minutes: int
    domain: DomainOut


class ConceptSourceOut(BaseModel):
    section_type: str | None
    source: SourceOut

    model_config = ConfigDict(from_attributes=True)


class ConceptRelationOut(BaseModel):
    relation_type: str
    concept: ConceptSummaryOut


class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    summary: str
    domain: DomainOut
    difficulty: str
    evidence_level: str
    estimated_reading_minutes: int
    status: str
    sections: list[ContentSection]
    tags: list[str]
    sources: list[ConceptSourceOut]


class ConceptListOut(BaseModel):
    items: list[ConceptSummaryOut]
    total: int
    page: int
    page_size: int


class ConceptCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    slug: str | None = None
    summary: str = Field(min_length=10)
    domain_slug: str
    difficulty: str = "beginner"
    evidence_level: str
    estimated_reading_minutes: int = 8
    status: str = "draft"
    sections: list[ContentSection] = []
    tags: list[str] = []
    source_ids: list[UUID] = []


class ImportRowError(BaseModel):
    item: str
    error: str


class ImportResult(BaseModel):
    created: int
    updated: int
    skipped: int
    errors: list[ImportRowError]
