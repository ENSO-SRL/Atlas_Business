from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CreateBookingRequest(BaseModel):
    customer_phone: str
    date: date
    start_time: str                   # "HH:MM"
    party_size: int
    bookable_object_id: UUID | None = None
    custom_fields: dict[str, Any] = {}

# ─── Public Businesses ───

class PublicBusinessDirectoryResponse(BaseModel):
    id: UUID
    category_id: UUID
    code: str
    name: str
    province: str
    municipality: str
    neighborhood: str
    street_address: str
    reference: str | None
    vertical_metadata: dict[str, Any] | None
    maps_url: str | None
    phone: str
    schedules: list[dict]

class PaginatedPublicBusinessDirectoryResponse(BaseModel):
    items: list[PublicBusinessDirectoryResponse]
    total: int
