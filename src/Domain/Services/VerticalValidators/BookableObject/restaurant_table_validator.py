from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class RestaurantTableValidator(IVerticalValidator):
    """
    Validador específico para la vertical de restaurantes en el contexto de mesas (objetos reservables).
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        if "table_area" in metadata and not isinstance(metadata["table_area"], str):
            return False, "El campo 'table_area' debe ser texto."

        if "is_accessible" in metadata and not isinstance(metadata["is_accessible"], bool):
            return False, "El campo 'is_accessible' debe ser booleano."

        if "is_combinable" in metadata and not isinstance(metadata["is_combinable"], bool):
            return False, "El campo 'is_combinable' debe ser booleano."

        if "combinable_with" in metadata:
            if not isinstance(metadata["combinable_with"], list):
                return False, "El campo 'combinable_with' debe ser una lista."
            if not all(isinstance(x, str) for x in metadata["combinable_with"]):
                return False, "Los elementos de 'combinable_with' deben ser texto."

        return True, None
