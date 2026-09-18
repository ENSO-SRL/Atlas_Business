from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CreateBookingRequest(BaseModel):
    date: str                         # "YYYY-MM-DD"
    start_time: str                   # "HH:MM"
    party_size: int
    bookable_object_id: UUID | None = None
    custom_fields: dict[str, Any] = {}
