from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class RestaurantServiceValidator(IVerticalValidator):
    """
    Validador específico para la vertical de Restaurantes a nivel de Servicio.
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        # restaurant_area
        if "restaurant_area" in metadata and not isinstance(metadata["restaurant_area"], str):
            return False, "El campo 'restaurant_area' debe ser texto."

        return True, None
