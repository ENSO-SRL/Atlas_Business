from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from src.Domain.Enums.publication_status import PublicationStatus

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
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name no puede estar vacío.")
            
        if self.occupation_duration_minutes < 1:
            raise ValueError("occupation_duration_minutes debe ser mayor o igual a 1.")
            
        if self.buffer_minutes < 0:
            raise ValueError("buffer_minutes no puede ser negativo.")
            
        if self.grid_interval_minutes < 1:
            raise ValueError("grid_interval_minutes debe ser mayor o igual a 1.")

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
