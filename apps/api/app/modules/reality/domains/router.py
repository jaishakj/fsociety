from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, DbSession
from app.modules.reality.domains import repository, service
from app.modules.reality.domains.schemas import DomainCreate, DomainOut

router = APIRouter()


@router.get("", response_model=list[DomainOut])
def list_domains(db: DbSession):
    return repository.list_domains(db)


@router.post("", response_model=DomainOut, status_code=201)
def create_domain(data: DomainCreate, db: DbSession, _admin: AdminUser):
    slug = data.slug or service.slugify(data.name)
    if repository.get_domain_by_slug(db, slug):
        raise HTTPException(status_code=400, detail="Slug already in use")
    return service.create_domain(db, data)
