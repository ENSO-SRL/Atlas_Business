from abc import ABC, abstractmethod


class IRncValidationService(ABC):
    @abstractmethod
    async def validate(self, rnc: str) -> bool:
        """Devuelve True si el RNC es válido ante la DGII (o fuente externa)."""
        pass
