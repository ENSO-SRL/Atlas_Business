from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.service_category import ServiceCategory


class IServiceCategoryRepository(ABC):

    @abstractmethod
    async def create(self, entity: ServiceCategory) -> ServiceCategory:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> ServiceCategory | None:
        pass

    @abstractmethod
    async def list_all(self, only_active: bool = True) -> list[ServiceCategory]:
        pass

    @abstractmethod
    async def update(self, entity: ServiceCategory) -> ServiceCategory:
        pass
