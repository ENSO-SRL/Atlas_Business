from dataclasses import dataclass, field
from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from uuid import UUID

from src.Domain.Enums.weekday import Weekday

class CalculationBasis(Enum):
    PER_BOOKING = "PER_BOOKING"
    PER_PERSON = "PER_PERSON"

@dataclass
class ServiceRate:
    """
    Define el precio por franja horaria y día de semana de un Service.
    """
    id: UUID
    service_id: UUID
    start_time: time
    end_time: time
    amount: Decimal
    calculation_basis: CalculationBasis
    weekdays: list[Weekday] = field(default_factory=list)
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time debe ser estrictamente menor que end_time.")
            
        if self.amount <= Decimal('0'):
            raise ValueError("amount debe ser mayor a cero.")
            
        if not self.weekdays:
            raise ValueError("weekdays no puede estar vacío.")
            
        if len(self.weekdays) != len(set(self.weekdays)):
            raise ValueError("weekdays no puede contener días duplicados.")

    def applies_at(self, weekday: Weekday, time_to_check: time) -> bool:
        """
        Verifica si la hora de inicio de una reserva cae dentro de esta tarifa.
        """
        if weekday not in self.weekdays:
            return False
        return self.start_time <= time_to_check < self.end_time
