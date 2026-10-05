from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class RestaurantTableValidator(IVerticalValidator):
    """
    Validador específico para la vertical de restaurantes en el contexto de mesas (objetos reservables).
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        # Ejemplo: validar area_name o accessible
        if "accessible" in metadata and not isinstance(metadata["accessible"], bool):
            return False, "El campo 'accessible' debe ser booleano."
                
        return True, None
