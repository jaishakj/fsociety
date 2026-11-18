from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import DbSession, get_current_user, get_db
from app.db.base import Base
from app.main import app
from app.modules.auth.models import User, UserRole, UserRoleAssignment
from app.modules.products.models import (
    Category,
    Product,
    ProductImage,
    ProductStatus,
    ProductVariant,
)


@pytest.fixture
def admin_product_client() -> Generator[tuple[TestClient, dict[str, UUID], dict[str, UUID]], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        User.__table__,
        UserRoleAssignment.__table__,
        Category.__table__,
        Product.__table__,
        ProductVariant.__table__,
        ProductImage.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    test_sessions = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    admin_id = uuid4()
    customer_id = uuid4()

    with test_sessions() as db:
        admin = User(
            id=admin_id,
            email="inventory-admin@example.com",
            password_hash="test",
            roles=[UserRoleAssignment(role=UserRole.ADMIN)],
        )
        customer = User(
            id=customer_id,
            email="inventory-customer@example.com",
            password_hash="test",
            roles=[UserRoleAssignment(role=UserRole.USER)],
        )
        category = Category(name="Dresses", slug="dresses")
        db.add_all([admin, customer, category])
        db.flush()

        products = [
            Product(
                name="Draft Blue Dress",
                slug="draft-blue-dress",
                price="1500.00",
                currency="INR",
                category_id=category.id,
                stock=0,
                status=ProductStatus.DRAFT,
                variants=[ProductVariant(size="XS", sku="DRAFT-BLUE-XS", stock=0)],
                images=[ProductImage(url="https://images.example/draft.jpg", alt="Blue dress")],
            ),
            Product(
                name="Published Blue Dress",
                slug="published-blue-dress",
                price="1800.00",
                currency="INR",
                category_id=category.id,
                stock=2,
                status=ProductStatus.PUBLISHED,
                variants=[ProductVariant(size="S", sku="PUBLISHED-BLUE-S", stock=2)],
            ),
            Product(
                name="Archived Red Dress",
                slug="archived-red-dress",
                price="1600.00",
                currency="INR",
                category_id=category.id,
                stock=0,
                status=ProductStatus.ARCHIVED,
            ),
        ]
        db.add_all(products)
        db.commit()
        product_ids = {product.slug: product.id for product in products}

    state = {"user_id": admin_id, "customer_id": customer_id}
    previous_overrides = app.dependency_overrides.copy()

    def override_db() -> Generator:
        with test_sessions() as db:
            yield db

    def override_current_user(db: DbSession):
        return db.get(User, state["user_id"])

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        yield TestClient(app), product_ids, state
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def test_admin_product_list_includes_all_statuses_and_variant_inventory(admin_product_client) -> None:
    client, product_ids, _state = admin_product_client

    response = client.get("/api/v1/admin/products")

    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 3
    products = {item["slug"]: item for item in result["items"]}
    assert {item["status"] for item in products.values()} == {"draft", "published", "archived"}
    assert products["draft-blue-dress"]["variants"][0]["size"] == "XS"
    assert products["draft-blue-dress"]["variants"][0]["stock"] == 0
    assert str(product_ids["published-blue-dress"]) == products["published-blue-dress"]["id"]


def test_admin_product_list_filters_status_and_search(admin_product_client) -> None:
    client, _product_ids, _state = admin_product_client

    response = client.get("/api/v1/admin/products", params={"status": "draft", "q": "blue"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["slug"] == "draft-blue-dress"


def test_admin_product_list_rejects_non_admin_users(admin_product_client) -> None:
    client, _product_ids, state = admin_product_client
    state["user_id"] = state["customer_id"]

    response = client.get("/api/v1/admin/products")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
