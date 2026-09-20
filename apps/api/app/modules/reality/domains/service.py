import re

from sqlalchemy.orm import Session

from app.modules.reality.domains.models import Domain
from app.modules.reality.domains.schemas import DomainCreate


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def create_domain(db: Session, data: DomainCreate) -> Domain:
    domain = Domain(
        name=data.name,
        slug=data.slug or slugify(data.name),
        description=data.description,
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain
