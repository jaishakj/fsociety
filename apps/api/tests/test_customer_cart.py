from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import DbSession, get_current_user, get_db
from app.db.base import Base
from app.main import app
from app.modules.auth.models import User
from app.modules.commerce.models import CustomerCart, CustomerCartItem
from app.modules.products.models import Category, Product, ProductImage, ProductStatus


@pytest.fixture
def cart_client() -> Generator[tuple[TestClient, dict[str, UUID], sessionmaker], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        User.__table__,
        Category.__table__,
        Product.__table__,
        ProductImage.__table__,
        CustomerCart.__table__,
        CustomerCartItem.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    user_id = uuid4()
    other_user_id = uuid4()
    with test_sessions() as db:
        db.add_all(
            [
                User(id=user_id, email="cart-user@example.com", password_hash="test"),
                User(id=other_user_id, email="other-cart-user@example.com", password_hash="test"),
            ]
        )
        shoes = Category(name="Footwear", slug="footwear")
        dresses = Category(name="Dresses", slug="dresses")
        sarees = Category(name="Sarees", slug="sarees")
        db.add_all([shoes, dresses, sarees])
        db.flush()
        products = [
            Product(
                name="Everyday Sandal",
                slug="everyday-sandal",
                price="900.00",
                currency="INR",
                stock=4,
                status=ProductStatus.PUBLISHED,
                category_id=shoes.id,
            ),
            Product(
                name="Cotton Dress",
                slug="cotton-dress",
                price="1800.00",
                currency="INR",
                stock=4,
                status=ProductStatus.PUBLISHED,
                category_id=dresses.id,
            ),
            Product(
                name="Silk Saree",
                slug="silk-saree",
                price="2400.00",
                currency="INR",
                stock=4,
                status=ProductStatus.PUBLISHED,
                category_id=sarees.id,
            ),
        ]
        db.add_all(products)
        db.commit()
        product_ids = {product.slug: product.id for product in products}

    state = {"user_id": user_id}
    previous_overrides = app.dependency_overrides.copy()

    def override_db() -> Generator:
        with test_sessions() as db:
            yield db

    def override_current_user(db: DbSession):
        return db.get(User, state["user_id"])

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        yield TestClient(app), {"user_id": user_id, "other_user_id": other_user_id, **product_ids}, test_sessions
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def test_cart_persists_server_products_sizes_and_isolated_by_user(cart_client) -> None:
    client, ids, test_sessions = cart_client
    response = client.put(
        "/api/v1/cart",
        json={
            "items": [
                {"product_id": str(ids["cotton-dress"]), "quantity": 1, "size": "XS"},
                {"product_id": str(ids["everyday-sandal"]), "quantity": 2},
            ]
        },
    )

    assert response.status_code == 200
    saved = response.json()
    assert len(saved["items"]) == 2
    assert {item["slug"]: item["size"] for item in saved["items"]} == {
        "cotton-dress": "XS",
        "everyday-sandal": None,
    }
    assert all(item["is_available"] for item in saved["items"])

    read_back = client.get("/api/v1/cart")
    assert read_back.status_code == 200
    assert read_back.json()["cart_id"] == saved["cart_id"]
    assert len(read_back.json()["items"]) == 2

    with test_sessions() as db:
        stored_cart = db.scalar(select(CustomerCart).where(CustomerCart.user_id == ids["user_id"]))
        assert stored_cart is not None
        assert len(stored_cart.items) == 2

    def act_as_other_user(db: DbSession):
        return db.get(User, ids["other_user_id"])

    app.dependency_overrides[get_current_user] = act_as_other_user
    other_user_cart = client.get("/api/v1/cart")
    assert other_user_cart.status_code == 200
    assert other_user_cart.json()["items"] == []


@pytest.mark.parametrize(
    "slug,size",
    [
        ("cotton-dress", None),
        ("silk-saree", "XS"),
        ("everyday-sandal", "M"),
    ],
)
def test_cart_rejects_invalid_category_size_combinations(cart_client, slug, size) -> None:
    client, ids, test_sessions = cart_client
    payload = {"product_id": str(ids[slug]), "quantity": 1}
    if size is not None:
        payload["size"] = size

    response = client.put("/api/v1/cart", json={"items": [payload]})

    assert response.status_code == 422
    assert response.json()["detail"] == "Select a valid size for each product"
    with test_sessions() as db:
        assert db.scalar(select(CustomerCart).where(CustomerCart.user_id == ids["user_id"])) is None


def test_cart_aggregates_duplicate_lines_before_stock_check(cart_client) -> None:
    client, ids, test_sessions = cart_client

    response = client.put(
        "/api/v1/cart",
        json={
            "items": [
                {"product_id": str(ids["silk-saree"]), "quantity": 3, "size": "S"},
                {"product_id": str(ids["silk-saree"]), "quantity": 2, "size": "M"},
            ]
        },
    )

    assert response.status_code == 409
    with test_sessions() as db:
        assert db.scalar(select(CustomerCart).where(CustomerCart.user_id == ids["user_id"])) is None


def test_cart_replacement_merges_duplicate_product_size_and_delete_clears(cart_client) -> None:
    client, ids, _test_sessions = cart_client
    payload = {
        "items": [
            {"product_id": str(ids["silk-saree"]), "quantity": 1, "size": "L"},
            {"product_id": str(ids["silk-saree"]), "quantity": 2, "size": "L"},
        ]
    }
    first = client.put("/api/v1/cart", json=payload)
    assert first.status_code == 200
    assert len(first.json()["items"]) == 1
    assert first.json()["items"][0]["quantity"] == 3

    replacement = client.put("/api/v1/cart", json={"items": [payload["items"][0]]})
    assert replacement.status_code == 200
    assert len(replacement.json()["items"]) == 1
    assert replacement.json()["items"][0]["quantity"] == 1

    cleared = client.delete("/api/v1/cart")
    assert cleared.status_code == 204
    assert client.get("/api/v1/cart").json()["items"] == []


def test_cart_endpoints_require_authentication(cart_client) -> None:
    client, _ids, _test_sessions = cart_client
    app.dependency_overrides.pop(get_current_user)

    assert client.get("/api/v1/cart").status_code == 401
    assert client.put("/api/v1/cart", json={"items": []}).status_code == 401
    assert client.delete("/api/v1/cart").status_code == 401
