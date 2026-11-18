from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ProductSize = Literal["XS", "S", "M", "L", "XL", "XXL"]


class CartMerchandiseQuoteLineIn(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=99)
    size: ProductSize | None = None


class CartMerchandiseQuoteIn(BaseModel):
    items: list[CartMerchandiseQuoteLineIn] = Field(min_length=1, max_length=50)


class CartMerchandiseQuoteLineOut(BaseModel):
    product_id: UUID
    name: str
    quantity: int
    size: ProductSize | None
    unit_price: Decimal
    line_subtotal: Decimal


class CartMerchandiseQuoteOut(BaseModel):
    currency: str
    items: list[CartMerchandiseQuoteLineOut]
    merchandise_subtotal: Decimal


class CustomerCartItemReplaceIn(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=99)
    size: ProductSize | None = None


class CustomerCartReplaceIn(BaseModel):
    items: list[CustomerCartItemReplaceIn] = Field(max_length=50)


class CustomerCartItemOut(BaseModel):
    id: UUID
    product_id: UUID
    name: str
    slug: str
    category_slug: str
    category_name: str
    quantity: int
    size: ProductSize | None
    unit_price: Decimal
    currency: str
    image_url: str | None
    is_available: bool


class CustomerCartOut(BaseModel):
    cart_id: UUID | None
    updated_at: datetime | None
    items: list[CustomerCartItemOut]
