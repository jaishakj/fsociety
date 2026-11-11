"""link shipping profiles to first-party customer accounts

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "customer_profiles",
        "clerk_user_id",
        existing_type=sa.String(length=128),
        nullable=True,
    )
    op.add_column(
        "customer_profiles",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("ix_customer_profiles_user_id", "customer_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    has_customer_accounts = bind.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM customer_profiles WHERE user_id IS NOT NULL)")
    ).scalar_one()
    if has_customer_accounts:
        raise RuntimeError("Cannot remove customer account links while customer profiles still exist")

    op.drop_index("ix_customer_profiles_user_id", table_name="customer_profiles")
    op.drop_column("customer_profiles", "user_id")
    op.alter_column(
        "customer_profiles",
        "clerk_user_id",
        existing_type=sa.String(length=128),
        nullable=False,
    )
