from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.Domain.Enums.gender import Gender


@dataclass
class BusinessCustomer:
    """
    Entidad que representa al cliente final que reserva servicios en un negocio.
    Su identidad principal en el contexto del negocio suele ser el teléfono.
    """
    id: UUID
    business_id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str | None = None
    gender: Gender | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
