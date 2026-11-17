"""persist authenticated customer carts

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_carts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_customer_carts_user_id"),
    )
    op.create_table(
        "customer_cart_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "cart_id",
            sa.Uuid(),
            sa.ForeignKey("customer_carts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("size", sa.String(length=3), server_default="", nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "cart_id",
            "product_id",
            "size",
            name="uq_customer_cart_items_cart_product_size",
        ),
        sa.CheckConstraint("quantity BETWEEN 1 AND 99", name="ck_customer_cart_items_quantity"),
        sa.CheckConstraint(
            "size IN ('', 'XS', 'S', 'M', 'L', 'XL', 'XXL')",
            name="ck_customer_cart_items_size",
        ),
    )
    op.create_index("ix_customer_cart_items_cart_id", "customer_cart_items", ["cart_id"])
    op.create_index("ix_customer_cart_items_product_id", "customer_cart_items", ["product_id"])


def downgrade() -> None:
    bind = op.get_bind()
    has_cart_items = bind.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM customer_cart_items)")
    ).scalar_one()
    has_customer_carts = bind.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM customer_carts)")
    ).scalar_one()
    if has_cart_items or has_customer_carts:
        raise RuntimeError("Cannot remove customer carts while saved cart data exists")

    op.drop_index("ix_customer_cart_items_product_id", table_name="customer_cart_items")
    op.drop_index("ix_customer_cart_items_cart_id", table_name="customer_cart_items")
    op.drop_table("customer_cart_items")
    op.drop_table("customer_carts")
