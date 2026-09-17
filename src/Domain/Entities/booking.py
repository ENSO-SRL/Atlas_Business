from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

@dataclass
class Booking:
    """
    Entidad que captura cada reserva realizada en el sistema.
    """
    id: UUID
    service_id: UUID
    bookable_object_id: UUID
    start_time: datetime
    end_time: datetime
    party_size: int
    calculated_amount: Decimal | None = None
    custom_fields: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if self.start_time.tzinfo is None or self.end_time.tzinfo is None:
            raise ValueError("start_time y end_time deben ser timezone-aware (preferentemente UTC).")
            
        if self.start_time >= self.end_time:
            raise ValueError("start_time debe ser estrictamente menor que end_time.")
            
        if self.party_size < 1:
            raise ValueError("party_size debe ser mayor o igual a 1.")
            
        if self.calculated_amount is not None and self.calculated_amount < Decimal('0'):
            raise ValueError("calculated_amount no puede ser negativo.")

    def overlaps_with(self, other: 'Booking', buffer_minutes: int) -> bool:
        """
        Verifica si esta reserva se solapa en el tiempo con otra reserva,
        teniendo en cuenta un tiempo de buffer.
        """
        buffer_td = timedelta(minutes=buffer_minutes)
        
        this_start = self.start_time
        this_end = self.end_time + buffer_td
        
        other_start = other.start_time
        other_end = other.end_time + buffer_td
        
        return (this_start < other_end) and (other_start < this_end)
