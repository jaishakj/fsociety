from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class CustomerProfile(UUIDMixin, TimestampMixin, Base):
    """Private shipping details linked to a verified Clerk customer ID."""

    __tablename__ = "customer_profiles"

    clerk_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(32))
    address_line_1: Mapped[str] = mapped_column(String(200))
    address_line_2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    state_or_region: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(24))
    country: Mapped[str] = mapped_column(String(100))
