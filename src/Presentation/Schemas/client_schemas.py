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
    address: str

class PaginatedPublicBusinessDirectoryResponse(BaseModel):
    items: list[PublicBusinessDirectoryResponse]
    total: int
