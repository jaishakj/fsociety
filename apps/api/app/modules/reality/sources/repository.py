from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.reality.sources.models import Source


def get_source(db: Session, source_id: UUID) -> Source | None:
    return db.get(Source, source_id)


def list_sources(db: Session) -> list[Source]:
    return list(db.scalars(select(Source).order_by(Source.title)))
