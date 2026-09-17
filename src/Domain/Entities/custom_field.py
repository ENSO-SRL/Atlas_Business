import re
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from uuid import UUID

class DataType(Enum):
    SHORT_TEXT = "SHORT_TEXT"
    LONG_TEXT = "LONG_TEXT"
    NUMBER = "NUMBER"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTI_CHOICE = "MULTI_CHOICE"
    YES_NO = "YES_NO"
    DATE = "DATE"

@dataclass
class CustomField:
    """
    Define campos adicionales tipados, solo descriptivos.
    No almacena valores, las respuestas se guardan en Booking.custom_fields.
    """
    id: UUID
    business_id: UUID
    label: str
    agent_note: str
    order: int
    required: bool
    visible_to_client: bool
    data_type: DataType
    service_id: UUID | None = None
    options: list[str] | None = None
    minimum: float | None = None
    maximum: float | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.label or not self.label.strip():
            raise ValueError("label no puede estar vacío.")
            
        if self.order < 0:
            raise ValueError("order no puede ser negativo.")

        # Validaciones dependientes del tipo de dato
        if self.data_type in (DataType.SINGLE_CHOICE, DataType.MULTI_CHOICE):
            if not self.options or len(self.options) < 2:
                raise ValueError("Para selección única o múltiple, options debe tener al menos 2 elementos.")
        else:
            if self.options is not None:
                raise ValueError(f"options debe ser None para el tipo de dato {self.data_type.value}.")

        if self.data_type == DataType.NUMBER:
            if self.minimum is None or self.maximum is None:
                raise ValueError("Para tipo número, minimum y maximum no pueden ser None.")
            if self.minimum > self.maximum:
                raise ValueError("minimum no puede ser mayor que maximum.")
        else:
            if self.minimum is not None or self.maximum is not None:
                raise ValueError(f"minimum y maximum deben ser None para el tipo de dato {self.data_type.value}.")

    def validate_value(self, value: str | int | float | bool | date | list[str]) -> bool:
        """
        Valida si un valor proporcionado cumple con el tipo de dato y las restricciones de este campo.
        Retorna True si es válido, False en caso contrario.
        """
        if value is None:
            return not self.required

        if self.data_type == DataType.SHORT_TEXT:
            return isinstance(value, str) and len(value) <= 255
            
        if self.data_type == DataType.LONG_TEXT:
            return isinstance(value, str)
            
        if self.data_type == DataType.NUMBER:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
            if self.minimum is not None and value < self.minimum:
                return False
            if self.maximum is not None and value > self.maximum:
                return False
            return True
            
        if self.data_type == DataType.SINGLE_CHOICE:
            return isinstance(value, str) and self.options is not None and value in self.options
            
        if self.data_type == DataType.MULTI_CHOICE:
            if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
                return False
            if self.options is None:
                return False
            return all(v in self.options for v in value)
            
        if self.data_type == DataType.YES_NO:
            return isinstance(value, bool)
            
        if self.data_type == DataType.DATE:
            if isinstance(value, date):
                return True
            if isinstance(value, str):
                try:
                    date.fromisoformat(value)
                    return True
                except ValueError:
                    return False
            return False
            
        return False
