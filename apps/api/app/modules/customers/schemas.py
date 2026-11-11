from pydantic import BaseModel, ConfigDict, Field


class ShippingProfileInput(BaseModel):
    phone_number: str = Field(min_length=7, max_length=32, pattern=r"^[+0-9() .-]+$")
    address_line_1: str = Field(min_length=3, max_length=200)
    address_line_2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state_or_region: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=2, max_length=24)
    country: str = Field(min_length=2, max_length=100)


class ShippingProfileOut(ShippingProfileInput):
    model_config = ConfigDict(from_attributes=True)


class AdminCustomerOut(ShippingProfileOut):
    id: str
    clerk_user_id: str
    created_at: str
    updated_at: str
