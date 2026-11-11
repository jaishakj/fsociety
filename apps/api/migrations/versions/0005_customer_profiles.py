"""store private customer shipping profiles

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("clerk_user_id", sa.String(length=128), nullable=False),
        sa.Column("phone_number", sa.String(length=32), nullable=False),
        sa.Column("address_line_1", sa.String(length=200), nullable=False),
        sa.Column("address_line_2", sa.String(length=200), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state_or_region", sa.String(length=100), nullable=False),
        sa.Column("postal_code", sa.String(length=24), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customer_profiles_clerk_user_id", "customer_profiles", ["clerk_user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_customer_profiles_clerk_user_id", table_name="customer_profiles")
    op.drop_table("customer_profiles")
