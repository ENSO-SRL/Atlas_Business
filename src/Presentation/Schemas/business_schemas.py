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

# ─── Bookings ───

class CreateInternalBookingRequest(BaseModel):
    service_id: UUID
    customer_id: UUID
    date: str
    start_time: str
    party_size: int = Field(..., gt=0)
    bookable_object_id: UUID | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)

# ─── Customers ───

class CreateCustomerRequest(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=30)
    email: EmailStr | None = None
    gender: str | None = None

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

# ─── Customers & Bookings ───

class BusinessCustomerResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str | None
    gender: str | None
    created_at: str | None

class PaginatedBusinessCustomerResponse(BaseModel):
    items: list[BusinessCustomerResponse]
    total: int

class CustomerBookingResponse(BaseModel):
    id: UUID
    service_id: UUID
    service_name: str
    bookable_object_name: str
    start_time: str
    end_time: str
    party_size: int
    calculated_amount: str | None
    created_at: str | None

class PaginatedCustomerBookingResponse(BaseModel):
    items: list[CustomerBookingResponse]
    total: int

# ─── User Businesses ───

class UserBusinessResponse(BaseModel):
    business_id: UUID
    business_name: str | None
    business_code: str | None
    roles: list[str]
    is_active: bool
    created_at: str | None

class PaginatedUserBusinessesResponse(BaseModel):
    items: list[UserBusinessResponse]
    total: int
