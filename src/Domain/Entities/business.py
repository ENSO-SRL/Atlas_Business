from dataclasses import dataclass, field
from datetime import datetime, time
from uuid import UUID

from src.Domain.Enums.platform import Platform
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Enums.weekday import Weekday

@dataclass
class BusinessSchedule:
    """
    Rango horario laboral para un día de la semana.
    Value Object usado dentro de Business.
    """
    weekday: Weekday
    opening_time: time
    closing_time: time

    def __post_init__(self):
        if self.opening_time >= self.closing_time:
            raise ValueError("opening_time debe ser menor a closing_time.")

@dataclass
class Business:
    """
    Entidad raíz del agregado. Representa un negocio afiliado en la plataforma.
    """
    id: UUID
    code: str
    name: str
    platform: Platform
    address: str
    phone: str
    rnc: str
    category_id: UUID
    agent_metadata_id: UUID
    verification_status: VerificationStatus = VerificationStatus.PENDING_VERIFICATION
    category_name: str | None = None
    aliases: list[str] = field(default_factory=list)
    schedules: list[BusinessSchedule] = field(default_factory=list)
    maps_url: str | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.code or not self.code.strip():
            raise ValueError("code no puede estar vacío.")
        if " " in self.code:
            raise ValueError("code no debe contener espacios.")
            
        if not self.name or not self.name.strip():
            raise ValueError("name no puede estar vacío.")
        
        if not self.rnc or not self.rnc.isdigit() or len(self.rnc) != 11:
            raise ValueError("rnc debe ser exactamente 11 dígitos numéricos.")
            
        if len(self.schedules) > 7:
            raise ValueError("schedules no puede tener más de 7 entradas.")
            
        dias = [s.weekday for s in self.schedules]
        if len(dias) != len(set(dias)):
            raise ValueError("schedules no puede contener días duplicados.")

    def is_publicly_visible(self) -> bool:
        """
        Indica si el negocio es visible públicamente para los clientes.
        """
        return self.verification_status == VerificationStatus.VERIFIED
