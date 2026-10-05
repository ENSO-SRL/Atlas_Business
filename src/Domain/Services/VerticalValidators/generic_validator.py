from typing import Any
from src.Domain.Ports.Services.i_vertical_validator import IVerticalValidator

class GenericVerticalValidator(IVerticalValidator):
    """
    Validador por defecto (fallback).
    Permite cualquier metadato (o podría exigir reglas básicas globales).
    """

    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        if not isinstance(metadata, dict):
            return False, "Los metadatos deben ser un diccionario JSON válido."
        return True, None
