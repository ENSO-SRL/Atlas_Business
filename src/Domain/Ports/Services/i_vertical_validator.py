from abc import ABC, abstractmethod
from typing import Any


class IVerticalValidator(ABC):
    """
    Puerto para la validación de metadatos específicos de la vertical (categoría del negocio).
    """

    @abstractmethod
    def validate(self, metadata: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Valida que el diccionario de metadatos cumpla con los requisitos del vertical.
        Retorna (True, None) si es válido, (False, mensaje_error) si es inválido.
        """
        pass
