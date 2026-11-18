from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.auth.models import User
from app.modules.commerce.models import CustomerCart, CustomerCartItem
from app.modules.products.models import Product, ProductStatus


def list_published_products_by_ids(db: Session, product_ids: set[UUID]) -> list[Product]:
    if not product_ids:
        return []

    statement = select(Product).where(
        Product.id.in_(product_ids),
        Product.status == ProductStatus.PUBLISHED,
    ).options(selectinload(Product.category), selectinload(Product.variants))
    return list(db.scalars(statement))


def lock_customer_row(db: Session, user_id: UUID) -> None:
    customer_id = db.scalar(select(User.id).where(User.id == user_id).with_for_update())
    if customer_id is None:
        raise HTTPException(status_code=404, detail="Customer account not found")


def get_customer_cart(db: Session, user_id: UUID) -> CustomerCart | None:
    statement = (
        select(CustomerCart)
        .options(
            selectinload(CustomerCart.items)
            .selectinload(CustomerCartItem.product)
            .selectinload(Product.category),
            selectinload(CustomerCart.items)
            .selectinload(CustomerCartItem.product)
            .selectinload(Product.images),
            selectinload(CustomerCart.items)
            .selectinload(CustomerCartItem.product)
            .selectinload(Product.variants),
        )
        .where(CustomerCart.user_id == user_id)
    )
    return db.scalar(statement)


def get_or_create_customer_cart(db: Session, user_id: UUID) -> CustomerCart:
    cart = db.scalar(
        select(CustomerCart)
        .where(CustomerCart.user_id == user_id)
        .with_for_update()
    )
    if cart is None:
        cart = CustomerCart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart


def list_purchasable_products_by_ids(
    db: Session,
    product_ids: set[UUID],
) -> list[Product]:
    if not product_ids:
        return []

    statement = (
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants),
        )
        .where(
            Product.id.in_(product_ids),
            Product.status == ProductStatus.PUBLISHED,
        )
        .order_by(Product.id)
        .with_for_update()
    )
    return list(db.scalars(statement))
