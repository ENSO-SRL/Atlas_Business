import re
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from src.Domain.Enums.system_role import SystemRole

@dataclass
class BusinessUser:
    """
    Usuario afiliado a un negocio con credenciales propias y roles de sistema.
    """
    id: UUID
    business_id: UUID
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    roles: list[SystemRole]
    phone: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.first_name or not self.first_name.strip():
            raise ValueError("first_name no puede estar vacío.")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("last_name no puede estar vacío.")
        
        # Validación básica de email
        if not self.email or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("email no tiene un formato válido.")
            
        if not self.hashed_password or not self.hashed_password.strip():
            raise ValueError("hashed_password no puede estar vacío.")
            
        if not self.roles:
            raise ValueError("El usuario debe tener al menos un rol asignado.")

    def has_role(self, role: SystemRole) -> bool:
        """Verifica si el usuario tiene un rol específico."""
        return role in self.roles
