from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DbSession
from app.modules.products import repository
from app.modules.products.models import ProductStatus
from app.modules.products.schemas import CategoryOut, ProductListOut, ProductOut

router = APIRouter()


@router.get("", response_model=ProductListOut)
def list_products(
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc)$"),
):
    items, total = repository.list_products(
        db,
        page=page,
        page_size=page_size,
        category_slug=category,
        search=q,
        status=ProductStatus.PUBLISHED,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )
    return ProductListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: DbSession):
    return repository.list_categories(db)


@router.get("/{slug}", response_model=ProductOut)
def get_product(slug: str, db: DbSession):
    product = repository.get_product_by_slug(db, slug)
    if not product or product.status != ProductStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
