from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    authors: list[str]
    url: str | None
    source_type: str
    publication_year: int | None
    publisher: str | None
    doi: str | None
    notes: str | None


class SourceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=500)
    authors: list[str] = []
    url: str | None = None
    source_type: str
    publication_year: int | None = None
    publisher: str | None = None
    doi: str | None = None
    notes: str | None = None
