from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class CourtRentalValidator(IVerticalValidator):
    """
    Validador específico para la vertical de servicios de alquiler de canchas.
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        # Ejemplo: validamos surface_type si existe
        if "surface_type" in metadata:
            val = metadata["surface_type"]
            if not isinstance(val, str):
                return False, "El campo 'surface_type' debe ser texto."
                
        return True, None
