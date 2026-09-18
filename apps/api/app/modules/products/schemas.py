from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    alt: str | None = None
    position: int


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str | None = None


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = None
    description: str | None = None
    price: Decimal = Field(gt=0)
    currency: str = "INR"
    category_id: UUID
    stock: int = Field(default=0, ge=0)
    status: str = "draft"
    images: list[str] = []


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    category_id: UUID | None = None
    stock: int | None = Field(default=None, ge=0)
    status: str | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    price: Decimal
    currency: str
    stock: int
    status: str
    category: CategoryOut
    images: list[ProductImageOut]


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int


class ImportRowError(BaseModel):
    row: int
    error: str


class ImportResult(BaseModel):
    created: int
    skipped: int
    errors: list[ImportRowError]
