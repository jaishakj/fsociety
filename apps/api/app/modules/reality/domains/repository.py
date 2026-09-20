from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.reality.domains.models import Domain


def get_domain_by_slug(db: Session, slug: str) -> Domain | None:
    return db.scalar(select(Domain).where(Domain.slug == slug))


def list_domains(db: Session) -> list[Domain]:
    return list(db.scalars(select(Domain).order_by(Domain.name)))
