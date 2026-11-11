from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class CustomerProfile(UUIDMixin, TimestampMixin, Base):
    """Private shipping details linked to an authenticated customer account."""

    __tablename__ = "customer_profiles"

    user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=True,
    )
    clerk_user_id: Mapped[str | None] = mapped_column(String(128), unique=True, index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(32))
    address_line_1: Mapped[str] = mapped_column(String(200))
    address_line_2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    state_or_region: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(24))
    country: Mapped[str] = mapped_column(String(100))
