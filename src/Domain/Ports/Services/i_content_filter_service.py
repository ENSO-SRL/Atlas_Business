from abc import ABC, abstractmethod


class IContentFilterService(ABC):
    @abstractmethod
    async def check(self, fields: dict[str, str]) -> list[str]:
        """
        Recibe dict {nombre_campo: texto} con solo los campos de texto libre a evaluar.
        Devuelve lista de coincidencias encontradas. Lista vacía = sin coincidencias.
        Ej: {"name": "...", "description": "..."} → ["name:palabra_prohibida"]
        """
        ...
