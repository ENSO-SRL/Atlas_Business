from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Any

# ─── Common ───

class ScheduleIn(BaseModel):
    weekday: str
    opening_time: str
    closing_time: str

class AgentMetadataIn(BaseModel):
    description: str | None = None
    establishment_policies: list[str] | None = None
    pre_booking_requirements: list[str] | None = None

# ─── Business ───

class RegisterBusinessRequest(BaseModel):
    code: str
    name: str
    rnc: str
    category_id: UUID
    platform: str
    address: str
    phone: str
    maps_url: str | None = None
    aliases: list[str] = []
    schedules: list[ScheduleIn] = []
    description: str
    establishment_policies: list[str] = []
    pre_booking_requirements: list[str] = []

class UpdateBusinessRequest(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    maps_url: str | None = None
    aliases: list[str] | None = None
    schedules: list[ScheduleIn] | None = None
    agent_metadata: AgentMetadataIn | None = None

# ─── Usuarios ───

class CreateUserRequest(BaseModel):
    email: EmailStr
    roles: list[str] = Field(..., min_items=1)
    # Requeridos solo si el usuario no existe:
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=30)
    password: str | None = Field(None, min_length=8)

class UpdateUserRequest(BaseModel):
    roles: list[str] | None = None
    is_active: bool | None = None

# ─── Services ───

class CreateServiceRequest(BaseModel):
    name: str
    category_id: UUID
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int = 0
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    auto_selection_criteria: str
    billing_nature: str
    agent_metadata: AgentMetadataIn
    rates: list[RateIn] | None = None

class UpdateServiceRequest(BaseModel):
    name: str | None = None
    category_id: UUID | None = None
    buffer_minutes: int | None = None
    grid_interval_minutes: int | None = None
    exposes_end_time: bool | None = None
    agent_metadata: AgentMetadataIn | None = None

# ─── Bookable Objects ───

class CreateBookableObjectRequest(BaseModel):
    name: str | None = None
    min_capacity: int
    max_capacity: int

class UpdateBookableObjectRequest(BaseModel):
    name: str | None = None
    min_capacity: int | None = None
    max_capacity: int | None = None
    is_active: bool | None = None

# ─── Rates ───

class RateIn(BaseModel):
    weekdays: list[str]
    start_time: str
    end_time: str
    amount: str
    calculation_basis: str

class ReplaceRatesRequest(BaseModel):
    rates: list[RateIn]

# ─── Custom Fields ───

class CreateCustomFieldRequest(BaseModel):
    label: str
    agent_note: str
    order: int
    required: bool
    visible_to_client: bool
    data_type: str
    options: list[str] | None = None
    minimum: float | None = None
    maximum: float | None = None
