from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Any
from uuid import UUID

from src.Domain.Entities.service_policies import (
    ArrivalAndConfirmationPolicy,
    ModificationPolicy,
    PaymentAndCancellationPolicy,
)
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Enums.weekday import Weekday

class DurationNature(Enum):
    FIXED = "FIXED"
    ESTIMATED = "ESTIMATED"
    INSTANT = "INSTANT"

class BillingNature(Enum):
    BILLABLE = "BILLABLE"
    NON_BILLABLE = "NON_BILLABLE"

class AutoSelectionCriteria(Enum):
    CLOSEST_MAX_CAPACITY = "CLOSEST_MAX_CAPACITY"

@dataclass
class ServiceSchedule:
    """
    Rango horario operativo específico para un servicio.
    """
    weekday: Weekday
    opening_time: time
    closing_time: time

    def __post_init__(self):
        if self.opening_time >= self.closing_time:
            raise ValueError("opening_time debe ser menor a closing_time.")

@dataclass
class Service:
    """
    Entidad hija de Business. Representa un servicio ofrecido que puede ser reservado.
    """
    id: UUID
    business_id: UUID
    name: str
    occupation_duration_minutes: int
    duration_nature: DurationNature
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    auto_selection_criteria: AutoSelectionCriteria
    billing_nature: BillingNature
    agent_metadata_id: UUID
    category_id: UUID
    publication_status: PublicationStatus = PublicationStatus.DRAFT
    rejection_reason: str | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    max_booking_window_days: int = 30
    min_booking_window_hours: int = 2
    max_daily_bookings_per_user: int = 1
    vertical_metadata: dict[str, Any] | None = None
    payment_cancellation_policy: PaymentAndCancellationPolicy | None = None
    modification_policy: ModificationPolicy | None = None
    arrival_confirmation_policy: ArrivalAndConfirmationPolicy | None = None
    schedules: list[ServiceSchedule] = field(default_factory=list)
    created_at: datetime | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name no puede estar vacío.")
            
        if self.occupation_duration_minutes < 1:
            raise ValueError("occupation_duration_minutes debe ser mayor o igual a 1.")
            
        if self.buffer_minutes < 0:
            raise ValueError("buffer_minutes no puede ser negativo.")
            
        if self.grid_interval_minutes < 1:
            raise ValueError("grid_interval_minutes debe ser mayor o igual a 1.")

        if self.max_booking_window_days < 1:
            raise ValueError("max_booking_window_days debe ser al menos 1.")

        if self.min_booking_window_hours < 0:
            raise ValueError("min_booking_window_hours no puede ser negativo.")

        if self.max_daily_bookings_per_user < 1:
            raise ValueError("max_daily_bookings_per_user debe ser al menos 1.")

        if len(self.schedules) > 7:
            raise ValueError("schedules no puede tener más de 7 entradas.")
            
        dias = [s.weekday for s in self.schedules]
        if len(dias) != len(set(dias)):
            raise ValueError("schedules no puede contener días duplicados para el servicio.")

    def is_bookable(self) -> bool:
        """
        Indica si el servicio está publicado y puede recibir reservas.
        """
        return self.publication_status == PublicationStatus.PUBLISHED

    def is_visible(self) -> bool:
        """
        Indica si el servicio es visible para los clientes. 
        En fase 1 es equivalente a is_bookable().
        """
        return self.is_bookable()
