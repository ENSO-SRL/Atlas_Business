from dataclasses import dataclass
from uuid import UUID


@dataclass
class BusinessCategory:
    """
    Catálogo administrativo de tipos de negocio (ej. Restaurante, Spa, Cancha de Pádel).
    """
    id: UUID
    name: str
    description: str | None = None
    is_active: bool = True
    is_deleted: bool = False

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name no puede estar vacío.")
