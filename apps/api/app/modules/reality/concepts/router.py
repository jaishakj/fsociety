from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.api.deps import AdminUser, DbSession
from app.modules.reality.concepts import repository, service
from app.modules.reality.concepts.importer import import_concepts
from app.modules.reality.concepts.models import ContentStatus, Difficulty
from app.modules.reality.concepts.schemas import (
    ConceptCreate,
    ConceptListOut,
    ConceptOut,
    ConceptRelationOut,
    ConceptSourceOut,
    ConceptSummaryOut,
    ImportResult,
)

router = APIRouter()

ALLOWED_IMPORT_EXTENSIONS = {".json", ".md"}
MAX_IMPORT_SIZE_BYTES = 5 * 1024 * 1024


@router.get("", response_model=ConceptListOut)
def list_concepts(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str | None = None,
    difficulty: str | None = None,
    q: str | None = None,
):
    items, total = repository.list_concepts(
        db,
        page=page,
        page_size=page_size,
        domain_slug=domain,
        difficulty=Difficulty(difficulty) if difficulty else None,
        search=q,
        status=ContentStatus.PUBLISHED,
    )
    return ConceptListOut(
        items=[ConceptSummaryOut.model_validate(service.concept_to_summary_dict(c)) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ConceptOut)
def get_concept(slug: str, db: DbSession):
    concept = repository.get_concept_by_slug(db, slug)
    if not concept or concept.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Concept not found")
    return service.concept_to_out_dict(concept)


@router.get("/{slug}/related", response_model=list[ConceptRelationOut])
def get_related(slug: str, db: DbSession):
    concept = repository.get_concept_by_slug(db, slug)
    if not concept or concept.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Concept not found")

    related = repository.get_related_concepts(db, concept.id)
    return [
        ConceptRelationOut(
            relation_type=relation_type,
            concept=service.concept_to_summary_dict(related_concept),
        )
        for relation_type, related_concept in related
    ]


@router.get("/{slug}/sources", response_model=list[ConceptSourceOut])
def get_sources(slug: str, db: DbSession):
    concept = repository.get_concept_by_slug(db, slug)
    if not concept or concept.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Concept not found")

    return [
        {"section_type": concept_source.section_type, "source": concept_source.source}
        for concept_source in concept.sources
    ]


@router.post("", response_model=ConceptOut, status_code=201)
def create_concept(data: ConceptCreate, db: DbSession, _admin: AdminUser):
    slug = data.slug or service.slugify(data.title)
    if repository.get_concept_by_slug(db, slug):
        raise HTTPException(status_code=400, detail="Slug already in use")

    try:
        concept = service.create_concept(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return service.concept_to_out_dict(concept)


@router.post("/import", response_model=ImportResult)
async def import_concepts_endpoint(db: DbSession, _admin: AdminUser, file: UploadFile = File(...)):
    from pathlib import Path

    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMPORT_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .json and .md files are accepted")

    content = await file.read()
    if len(content) > MAX_IMPORT_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        return import_concepts(db, file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
