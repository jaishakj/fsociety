from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.core.config import settings
from app.modules.customers.models import CustomerProfile
from app.modules.customers.schemas import AdminCustomerOut, ShippingProfileInput, ShippingProfileOut

router = APIRouter()


@router.get("/profile", response_model=ShippingProfileOut)
def get_profile(db: DbSession, current_user: CurrentUser):
    profile = db.scalar(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Shipping profile not found")
    return profile


@router.put("/profile", response_model=ShippingProfileOut)
def save_profile(data: ShippingProfileInput, db: DbSession, current_user: CurrentUser):
    profile = db.scalar(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    if profile is None:
        profile = CustomerProfile(user_id=current_user.id, **data.model_dump())
        db.add(profile)
    else:
        for key, value in data.model_dump().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/admin/customers", response_model=list[AdminCustomerOut])
def list_customer_profiles(
    db: DbSession,
    admin: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Restrict the customer directory to the explicitly configured store owner."""
    owner_email = (settings.customer_data_owner_email or "").strip().casefold()
    if not owner_email:
        raise HTTPException(status_code=503, detail="Store owner access is not configured")
    if admin.email.strip().casefold() != owner_email:
        raise HTTPException(status_code=403, detail="Store owner access required")
    return db.scalars(
        select(CustomerProfile)
        .order_by(CustomerProfile.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
