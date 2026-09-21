import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class User:
    """
    Entidad de identidad. Email único global. Contiene datos personales y credenciales.
    No está vinculada a ningún negocio en particular (la relación se da en BusinessUser).
    """
    id: UUID
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    phone: str | None = None
    is_email_verified: bool = False
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

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
