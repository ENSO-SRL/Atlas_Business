from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class BookableObject:
    """
    Unidad física reservable (cancha, mesa, tee) que pertenece a un Service.
    """
    id: UUID
    service_id: UUID
    min_capacity: int
    max_capacity: int
    is_active: bool = True
    name: str | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if self.min_capacity < 1:
            raise ValueError("min_capacity debe ser mayor o igual a 1.")
            
        if self.max_capacity < self.min_capacity:
            raise ValueError("max_capacity debe ser mayor o igual a min_capacity.")

    def qualifies_for(self, party_size: int) -> bool:
        """
        Verifica si este objeto tiene la capacidad para acomodar a una cantidad de personas.
        """
        return self.min_capacity <= party_size <= self.max_capacity
