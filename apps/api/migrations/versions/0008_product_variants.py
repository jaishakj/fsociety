"""add size-specific product inventory

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("size", sa.String(length=3), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("product_id", "size", name="uq_product_variants_product_size"),
        sa.UniqueConstraint("sku", name="uq_product_variants_sku"),
        sa.CheckConstraint(
            "size IN ('XS', 'S', 'M', 'L', 'XL', 'XXL')",
            name="ck_product_variants_size",
        ),
        sa.CheckConstraint("stock >= 0", name="ck_product_variants_stock"),
    )
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])


def downgrade() -> None:
    bind = op.get_bind()
    has_variants = bind.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM product_variants)")
    ).scalar_one()
    if has_variants:
        raise RuntimeError("Cannot remove size-specific inventory while product variants exist")

    op.drop_index("ix_product_variants_product_id", table_name="product_variants")
    op.drop_table("product_variants")
