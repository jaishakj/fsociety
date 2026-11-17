from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.modules.products.models import Product


class CustomerCart(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customer_carts"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    items: Mapped[list["CustomerCartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
        order_by="CustomerCartItem.created_at",
    )


class CustomerCartItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customer_cart_items"
    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_id",
            "size",
            name="uq_customer_cart_items_cart_product_size",
        ),
        CheckConstraint("quantity BETWEEN 1 AND 99", name="ck_customer_cart_items_quantity"),
        CheckConstraint(
            "size IN ('', 'XS', 'S', 'M', 'L', 'XL', 'XXL')",
            name="ck_customer_cart_items_size",
        ),
    )

    cart_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("customer_carts.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
    )
    # Empty string means the item has no size selection (for example footwear).
    # It is non-null so PostgreSQL's unique constraint also handles unsized items.
    size: Mapped[str] = mapped_column(String(3), default="", server_default="")
    quantity: Mapped[int] = mapped_column(Integer)

    cart: Mapped[CustomerCart] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()
