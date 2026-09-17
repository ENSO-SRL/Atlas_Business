from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.business import Business


class IBusinessRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Business | None:
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Business | None:
        """Usado en RegisterBusinessUseCase para verificar unicidad del code."""
        ...

    @abstractmethod
    async def create(self, entity: Business) -> Business:
        """Usado únicamente en RegisterBusinessUseCase."""
        ...

    @abstractmethod
    async def update(self, entity: Business) -> Business:
        ...
