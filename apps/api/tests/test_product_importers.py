import json
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.modules.products.importers import import_products
from app.modules.products.models import Category, Product, ProductImage, ProductVariant


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
        session.add_all(
            [
                Category(name="Dresses", slug="dresses"),
                Category(name="Tops", slug="tops"),
                Category(name="Footwear", slug="footwear"),
            ]
        )
        session.commit()
        yield session
    engine.dispose()


def test_json_imports_size_stock_and_keeps_valid_rows_after_a_bad_row(db: Session) -> None:
    content = json.dumps(
        {
            "products": [
                {
                    "name": "Cotton Dress",
                    "price": "1500.00",
                    "category_slug": "dresses",
                    "variants": [
                        {"size": "XS", "stock": 2},
                        {"size": "M", "stock": 3},
                    ],
                },
                {
                    "name": "Linen Top",
                    "price": "850.00",
                    "category_slug": "tops",
                    "variants": [{"size": "XS", "stock": 1}],
                },
                {
                    "name": "Everyday Sandal",
                    "price": "900.00",
                    "category_slug": "footwear",
                    "stock": 4,
                },
            ]
        }
    ).encode()

    result = import_products(db, "products.json", content)

    assert result.created == 2
    assert result.skipped == 0
    assert len(result.errors) == 1
    assert result.errors[0].row == 2
    assert "not valid" in result.errors[0].error

    dress = db.scalar(select(Product).where(Product.slug == "cotton-dress"))
    sandal = db.scalar(select(Product).where(Product.slug == "everyday-sandal"))
    assert dress is not None and dress.stock == 5
    assert {variant.size: variant.stock for variant in dress.variants} == {"XS": 2, "M": 3}
    assert all(variant.sku for variant in dress.variants)
    assert sandal is not None and sandal.stock == 4 and sandal.variants == []


def test_csv_import_accepts_json_variant_cell(db: Session) -> None:
    content = (
        b'name,price,category_slug,variants\n'
        b'"Summer Dress",1200.00,dresses,"[{""size"":""S"",""stock"":2}]"\n'
    )

    result = import_products(db, "products.csv", content)

    assert result.created == 1
    assert result.errors == []
    product = db.scalar(select(Product).where(Product.slug == "summer-dress"))
    assert product is not None and product.stock == 2
    assert [(variant.size, variant.stock) for variant in product.variants] == [("S", 2)]
