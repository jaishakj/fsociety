from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession
from app.modules.reality.sources import repository
from app.modules.reality.sources.models import Source, SourceType
from app.modules.reality.sources.schemas import SourceCreate, SourceOut

router = APIRouter()


@router.get("", response_model=list[SourceOut])
def list_sources(db: DbSession):
    return repository.list_sources(db)


@router.post("", response_model=SourceOut, status_code=201)
def create_source(data: SourceCreate, db: DbSession, _admin: AdminUser):
    source = Source(
        title=data.title,
        authors=data.authors,
        url=data.url,
        source_type=SourceType(data.source_type),
        publication_year=data.publication_year,
        publisher=data.publisher,
        doi=data.doi,
        notes=data.notes,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
