from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.bookable_object import BookableObject


class IBookableObjectRepository(ABC):
    @abstractmethod
    async def list_by_service(self, service_id: UUID) -> list[BookableObject]:
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID, service_id: UUID) -> BookableObject | None:
        ...

    @abstractmethod
    async def create(self, entity: BookableObject) -> BookableObject:
        ...

    @abstractmethod
    async def update(self, entity: BookableObject) -> BookableObject:
        ...
