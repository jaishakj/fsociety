from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ProductSize = Literal["XS", "S", "M", "L", "XL", "XXL"]


class ProductVariantWrite(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    size: ProductSize
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    stock: int = Field(ge=0)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    size: ProductSize
    sku: str
    stock: int


def _validate_variant_collection(variants: list[ProductVariantWrite]) -> None:
    sizes = [variant.size for variant in variants]
    if len(sizes) != len(set(sizes)):
        raise ValueError("Each size can only have one inventory entry")

    skus = [variant.sku for variant in variants if variant.sku]
    if len(skus) != len(set(skus)):
        raise ValueError("Variant SKUs must be unique")


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


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100, strip_whitespace=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = None
    description: str | None = None
    price: Decimal = Field(gt=0)
    currency: str = "INR"
    category_id: UUID
    stock: int | None = Field(default=None, ge=0)
    status: str = "draft"
    variants: list[ProductVariantWrite] = Field(default_factory=list, max_length=6)
    images: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_variants(self):
        _validate_variant_collection(self.variants)
        if self.variants and self.stock is not None:
            variant_stock = sum(variant.stock for variant in self.variants)
            if self.stock != variant_stock:
                raise ValueError("Product stock must equal the sum of its variant stock")
        return self


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    category_id: UUID | None = None
    stock: int | None = Field(default=None, ge=0)
    status: str | None = None
    variants: list[ProductVariantWrite] | None = Field(default=None, max_length=6)

    @model_validator(mode="after")
    def validate_variants(self):
        if self.variants is not None:
            _validate_variant_collection(self.variants)
            if not self.variants and self.stock is None:
                raise ValueError("Provide legacy stock when removing all product variants")
            if self.variants and self.stock is not None:
                variant_stock = sum(variant.stock for variant in self.variants)
                if self.stock != variant_stock:
                    raise ValueError("Product stock must equal the sum of its variant stock")
        return self


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
    variants: list[ProductVariantOut] = Field(default_factory=list)


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
