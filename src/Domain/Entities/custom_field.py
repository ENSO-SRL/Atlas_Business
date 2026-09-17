import re
from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID

from src.Domain.Enums.data_type import DataType

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

    def validate_response(self, value: str | int | float | bool | date | list[str] | None) -> tuple[bool, str]:
        """
        Valida si un valor proporcionado cumple con el tipo de dato y las restricciones de este campo.
        Retorna (True, "") si es válido, (False, mensaje) en caso contrario.
        """
        if value is None:
            if self.required:
                return False, f"El campo '{self.label}' es requerido."
            return True, ""

        if self.data_type == DataType.SHORT_TEXT:
            if not isinstance(value, str):
                return False, f"El valor para '{self.label}' debe ser texto."
            if len(value) > 255:
                return False, f"El valor para '{self.label}' no puede exceder 255 caracteres."
            return True, ""
            
        if self.data_type == DataType.LONG_TEXT:
            if not isinstance(value, str):
                return False, f"El valor para '{self.label}' debe ser texto."
            return True, ""
            
        if self.data_type == DataType.NUMBER:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, f"El valor para '{self.label}' debe ser numérico."
            if self.minimum is not None and value < self.minimum:
                return False, f"El valor para '{self.label}' debe ser al menos {self.minimum}."
            if self.maximum is not None and value > self.maximum:
                return False, f"El valor para '{self.label}' debe ser como máximo {self.maximum}."
            return True, ""
            
        if self.data_type == DataType.SINGLE_CHOICE:
            if not isinstance(value, str) or self.options is None or value not in self.options:
                return False, f"El valor '{value}' no es una opción válida para '{self.label}'."
            return True, ""
            
        if self.data_type == DataType.MULTI_CHOICE:
            if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
                return False, f"El valor para '{self.label}' debe ser una lista de textos."
            if self.options is None or not all(v in self.options for v in value):
                return False, f"Uno o más valores no son opciones válidas para '{self.label}'."
            return True, ""
            
        if self.data_type == DataType.YES_NO:
            if not isinstance(value, bool):
                return False, f"El valor para '{self.label}' debe ser booleano (sí/no)."
            return True, ""
            
        if self.data_type == DataType.DATE:
            if isinstance(value, date):
                return True, ""
            if isinstance(value, str):
                try:
                    date.fromisoformat(value)
                    return True, ""
                except ValueError:
                    return False, f"El valor para '{self.label}' debe ser una fecha válida en formato YYYY-MM-DD."
            return False, f"El valor para '{self.label}' debe ser una fecha válida."
            
        return False, f"Tipo de dato desconocido para el campo '{self.label}'."
