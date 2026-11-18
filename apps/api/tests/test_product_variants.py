from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.modules.products import service
from app.modules.products.models import Category, Product, ProductImage, ProductVariant
from app.modules.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductVariantWrite,
)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(
        engine,
        tables=[
            Category.__table__,
            Product.__table__,
            ProductVariant.__table__,
            ProductImage.__table__,
        ],
    )
    sessions = sessionmaker(bind=engine, expire_on_commit=False)
    with sessions() as session:
        yield session
    engine.dispose()


def make_category(db: Session, *, name: str = "Dresses", slug: str = "dresses") -> Category:
    category = Category(name=name, slug=slug)
    db.add(category)
    db.commit()
    return category


def make_product(
    db: Session,
    category: Category,
    *,
    variants: list[ProductVariantWrite] | None = None,
) -> Product:
    return service.create_product(
        db,
        ProductCreate(
            name="Cotton Dress",
            slug=f"cotton-dress-{category.slug}",
            price=Decimal("1500.00"),
            category_id=category.id,
            variants=variants or [],
        ),
    )


def test_create_product_sets_aggregate_stock_and_stable_skus(db: Session) -> None:
    category = make_category(db)

    product = make_product(
        db,
        category,
        variants=[
            ProductVariantWrite(size="XS", stock=2),
            ProductVariantWrite(size="M", stock=4),
        ],
    )

    assert product.stock == 6
    assert [(variant.size, variant.stock) for variant in product.variants] == [
        ("M", 4),
        ("XS", 2),
    ]
    assert all(variant.sku.startswith("COTTONDRESSDRESSES-") for variant in product.variants)
    assert len({variant.sku for variant in product.variants}) == 2


def test_variant_sizes_follow_product_category(db: Session) -> None:
    tops = make_category(db, name="Tops", slug="tops")

    with pytest.raises(HTTPException) as error:
        make_product(
            db,
            tops,
            variants=[ProductVariantWrite(size="XS", stock=1)],
        )

    assert error.value.status_code == 422
    assert "not valid" in error.value.detail


def test_variant_sizes_cannot_be_duplicated_in_product_input() -> None:
    with pytest.raises(ValidationError, match="one inventory entry"):
        ProductCreate(
            name="Cotton Dress",
            slug="cotton-dress",
            price=Decimal("1500.00"),
            category_id="00000000-0000-0000-0000-000000000001",
            variants=[
                ProductVariantWrite(size="M", stock=1),
                ProductVariantWrite(size="M", stock=2),
            ],
        )


def test_category_change_cannot_invalidate_managed_sizes(db: Session) -> None:
    dresses = make_category(db)
    tops = make_category(db, name="Tops", slug="tops")
    product = make_product(db, dresses, variants=[ProductVariantWrite(size="XS", stock=1)])

    with pytest.raises(HTTPException) as error:
        service.update_product(db, product, ProductUpdate(category_id=tops.id))

    assert error.value.status_code == 422
    assert "Update or remove variants" in error.value.detail


def test_variant_skus_must_not_conflict_with_another_product(db: Session) -> None:
    category = make_category(db)
    make_product(db, category, variants=[ProductVariantWrite(size="S", sku="DRESS-S", stock=1)])

    with pytest.raises(HTTPException) as error:
        service.create_product(
            db,
            ProductCreate(
                name="Evening Dress",
                slug="evening-dress",
                price=Decimal("1800.00"),
                category_id=category.id,
                variants=[ProductVariantWrite(size="S", sku="DRESS-S", stock=1)],
            ),
        )

    assert error.value.status_code == 409
    assert error.value.detail == "A variant SKU is already in use"


def test_variant_updates_keep_product_stock_in_sync_and_guard_stock_removal(db: Session) -> None:
    category = make_category(db)
    product = make_product(
        db,
        category,
        variants=[
            ProductVariantWrite(size="S", stock=2),
            ProductVariantWrite(size="M", stock=3),
        ],
    )

    service.update_product(
        db,
        product,
        ProductUpdate(
            variants=[
                ProductVariantWrite(size="S", stock=1),
                ProductVariantWrite(size="M", stock=4),
            ]
        ),
    )
    assert product.stock == 5
    assert {variant.size: variant.stock for variant in product.variants} == {"S": 1, "M": 4}

    with pytest.raises(HTTPException) as error:
        service.update_product(
            db,
            product,
            ProductUpdate(variants=[ProductVariantWrite(size="S", stock=1)], stock=1),
        )
    assert error.value.status_code == 409
    assert "stock to zero" in error.value.detail

    service.update_product(
        db,
        product,
        ProductUpdate(
            variants=[
                ProductVariantWrite(size="S", stock=1),
                ProductVariantWrite(size="M", stock=0),
            ]
        ),
    )
    service.update_product(
        db,
        product,
        ProductUpdate(variants=[ProductVariantWrite(size="S", stock=1)], stock=1),
    )
    assert product.stock == 1
    assert [(variant.size, variant.stock) for variant in product.variants] == [("S", 1)]


def test_legacy_stock_cannot_be_changed_while_variants_are_managed(db: Session) -> None:
    category = make_category(db)
    product = make_product(db, category, variants=[ProductVariantWrite(size="M", stock=2)])

    with pytest.raises(HTTPException) as error:
        service.update_product(db, product, ProductUpdate(stock=9))

    assert error.value.status_code == 422
    assert "variants field" in error.value.detail
