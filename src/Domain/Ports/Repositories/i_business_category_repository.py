from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.business_category import BusinessCategory


class IBusinessCategoryRepository(ABC):

    @abstractmethod
    async def create(self, entity: BusinessCategory) -> BusinessCategory:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> BusinessCategory | None:
        pass

    @abstractmethod
    async def list_all(self, only_active: bool = True) -> list[BusinessCategory]:
        pass

    @abstractmethod
    async def update(self, entity: BusinessCategory) -> BusinessCategory:
        pass
