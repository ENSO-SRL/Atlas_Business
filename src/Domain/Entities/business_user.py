from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.Domain.Entities.user import User
from src.Domain.Enums.system_role import SystemRole

@dataclass
class BusinessUser:
    """
    Relación entre un User y un Business, junto con los roles que tiene en ese contexto.
    No almacena datos personales (esos viven en User).
    """
    id: UUID
    user_id: UUID
    business_id: UUID
    roles: list[SystemRole]
    is_active: bool = True
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    
    # Datos de navegación (opcionalmente poblados por repositorios para evitar un 2do query)
    user: User | None = None
    business_name: str | None = None
    business_code: str | None = None

    def __post_init__(self):
        if not self.roles:
            raise ValueError("El usuario de negocio debe tener al menos un rol asignado.")

    def has_role(self, role: SystemRole) -> bool:
        """Verifica si el usuario tiene un rol específico en este negocio."""
        return role in self.roles

