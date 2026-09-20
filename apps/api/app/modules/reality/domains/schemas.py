from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DomainOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None = None


class DomainCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str | None = None
    description: str | None = None
