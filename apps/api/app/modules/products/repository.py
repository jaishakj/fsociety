from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.products.models import Category, Product, ProductStatus


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.scalar(select(Category).where(Category.slug == slug))


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


def get_product_by_slug(db: Session, slug: str) -> Product | None:
    stmt = (
        select(Product)
        .options(selectinload(Product.images), selectinload(Product.category))
        .where(Product.slug == slug)
    )
    return db.scalar(stmt)


def get_product_by_id(db: Session, product_id: UUID) -> Product | None:
    stmt = (
        select(Product)
        .options(selectinload(Product.images), selectinload(Product.category))
        .where(Product.id == product_id)
    )
    return db.scalar(stmt)


def list_products(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    category_slug: str | None = None,
    search: str | None = None,
    status: ProductStatus | None = ProductStatus.PUBLISHED,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "newest",
) -> tuple[list[Product], int]:
    stmt = select(Product).options(
        selectinload(Product.images), selectinload(Product.category)
    )

    if status is not None:
        stmt = stmt.where(Product.status == status)
    if category_slug:
        stmt = stmt.join(Category).where(Category.slug == category_slug)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.description.ilike(like)))
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    if sort == "price_asc":
        stmt = stmt.order_by(Product.price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Product.price.desc())
    else:
        stmt = stmt.order_by(Product.created_at.desc())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    items = list(db.scalars(stmt))
    return items, total
