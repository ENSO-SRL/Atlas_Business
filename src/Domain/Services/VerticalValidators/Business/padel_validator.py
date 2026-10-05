from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class PadelVerticalValidator(IVerticalValidator):
    """
    Validador específico para la vertical de Padel.
    Ejemplo de validación: puede requerir el número total de canchas de padel.
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
            
        # Ejemplo: validamos que si envían total_courts, sea un entero válido
        if "total_courts" in metadata:
            val = metadata["total_courts"]
            if not isinstance(val, int) or val <= 0:
                return False, "El campo 'total_courts' debe ser un número entero mayor a 0."
                
        # Más reglas específicas podrían ir aquí
        
        return True, None
