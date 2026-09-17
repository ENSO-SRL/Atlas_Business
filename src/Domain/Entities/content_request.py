from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

class ContentRequestStatus(Enum):
    """
    Estados posibles para una solicitud de edición de contenido (ContentRequest).
    """
    PENDING_FILTER = "PENDING_FILTER"
    APPROVED = "APPROVED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"

@dataclass
class ContentRequest:
    """
    Solicitud de edición sobre un Service ya publicado (patrón shadow edit).
    La versión publicada queda intacta mientras la edición está pendiente.
    """
    id: UUID
    service_id: UUID
    payload: dict[str, Any]
    status: ContentRequestStatus = ContentRequestStatus.PENDING_FILTER
    filter_matches: list[str] = field(default_factory=list)
    rejection_reason: str | None = None
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.payload:
            raise ValueError("payload no puede estar vacío en una solicitud de edición.")
            
        if self.status == ContentRequestStatus.REJECTED and not self.rejection_reason:
            raise ValueError("rejection_reason es obligatorio si la solicitud fue rechazada.")
            
        if self.status in (ContentRequestStatus.APPROVED, ContentRequestStatus.REJECTED, ContentRequestStatus.UNDER_REVIEW):
            # El filtro ya corrió, así que 'filter_matches' ya debería estar validado según lógica de negocio.
            # En el dominio solo podemos asegurar que el estado sea coherente.
            pass

    def is_pending(self) -> bool:
        """
        Indica si la solicitud aún está esperando resolución o procesamiento.
        """
        return self.status in (ContentRequestStatus.PENDING_FILTER, ContentRequestStatus.UNDER_REVIEW)
