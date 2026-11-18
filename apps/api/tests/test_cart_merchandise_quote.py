from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.api.deps import get_db
from app.main import app
from app.modules.commerce.repository import list_published_products_by_ids
from app.modules.products.models import ProductStatus


@pytest.fixture
def client():
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: object()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def make_product(
    product_id: UUID,
    *,
    name: str = "Linen Saree",
    price: str = "1299.50",
    stock: int = 5,
    currency: str = "INR",
    category_slug: str = "sarees",
    category_name: str = "Sarees",
    variants: list | None = None,
):
    return SimpleNamespace(
        id=product_id,
        name=name,
        price=Decimal(price),
        stock=stock,
        currency=currency,
        status=ProductStatus.PUBLISHED,
        category=SimpleNamespace(slug=category_slug, name=category_name),
        variants=variants or [],
    )


def test_quote_uses_published_server_prices_and_decimal_arithmetic(client, monkeypatch) -> None:
    product_id = uuid4()
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [make_product(product_id)],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={"items": [{"product_id": str(product_id), "quantity": 2, "size": "M"}]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "currency": "INR",
        "items": [
            {
                "product_id": str(product_id),
                "name": "Linen Saree",
                "quantity": 2,
                "size": "M",
                "unit_price": "1299.50",
                "line_subtotal": "2599.00",
            }
        ],
        "merchandise_subtotal": "2599.00",
    }


def test_quote_aggregates_duplicate_product_lines_before_stock_check(client, monkeypatch) -> None:
    product_id = uuid4()
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [make_product(product_id, stock=3)],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={
            "items": [
                {"product_id": str(product_id), "quantity": 2, "size": "M"},
                {"product_id": str(product_id), "quantity": 2, "size": "L"},
            ]
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Requested quantity is unavailable"


def test_quote_rejects_unpublished_or_unknown_products(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={"items": [{"product_id": str(uuid4()), "quantity": 1}]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "One or more products are unavailable"


def test_quote_rejects_mixed_currency_baskets(client, monkeypatch) -> None:
    first_id = uuid4()
    second_id = uuid4()
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [
            make_product(first_id),
            make_product(second_id, currency="USD"),
        ],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={
            "items": [
                {"product_id": str(first_id), "quantity": 1, "size": "M"},
                {"product_id": str(second_id), "quantity": 1, "size": "M"},
            ]
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Cart products must use the same currency"


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{"product_id": str(uuid4()), "quantity": 0}],
        [{"product_id": "not-a-uuid", "quantity": 1}],
    ],
)
def test_quote_validates_cart_lines(client, monkeypatch, items) -> None:
    def unexpected_repository_call(_db, _ids):
        pytest.fail("Invalid request reached the product repository")

    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        unexpected_repository_call,
    )

    response = client.post("/api/v1/cart/merchandise-quote", json={"items": items})

    assert response.status_code == 422


def test_product_lookup_scopes_quote_to_published_catalog_items() -> None:
    class CapturingSession:
        statement = None

        def scalars(self, statement):
            self.statement = statement
            return []

    db = CapturingSession()
    product_id = uuid4()

    assert list_published_products_by_ids(db, {product_id}) == []

    compiled = db.statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert "products.id IN" in sql
    assert "products.status =" in sql
    assert ProductStatus.PUBLISHED in compiled.params.values()


@pytest.mark.parametrize(
    ("category_slug", "category_name", "size", "expected_status"),
    [
        ("dresses", "Dresses", "XS", 200),
        ("tops", "Tops", "XS", 422),
        ("footwear", "Footwear", None, 200),
        ("sarees", "Sarees", None, 422),
    ],
)
def test_quote_validates_selected_size_for_product_category(
    client,
    monkeypatch,
    category_slug,
    category_name,
    size,
    expected_status,
) -> None:
    product_id = uuid4()
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [
            make_product(
                product_id,
                category_slug=category_slug,
                category_name=category_name,
            )
        ],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={"items": [{"product_id": str(product_id), "quantity": 1, "size": size}]},
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["items"][0]["size"] == size


def test_quote_requires_size_for_clothing_products(client, monkeypatch) -> None:
    product_id = uuid4()
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [make_product(product_id)],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={"items": [{"product_id": str(product_id), "quantity": 1}]},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Select a valid size for each product"


def test_quote_checks_stock_for_the_selected_size(client, monkeypatch) -> None:
    product_id = uuid4()
    product = make_product(
        product_id,
        stock=5,
        variants=[
            SimpleNamespace(size="M", stock=1),
            SimpleNamespace(size="L", stock=4),
        ],
    )
    monkeypatch.setattr(
        "app.modules.commerce.router.repository.list_published_products_by_ids",
        lambda _db, _ids: [product],
    )

    response = client.post(
        "/api/v1/cart/merchandise-quote",
        json={"items": [{"product_id": str(product_id), "quantity": 2, "size": "M"}]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Requested size is unavailable"
