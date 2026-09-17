from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.custom_field import CustomField


class ICustomFieldRepository(ABC):
    @abstractmethod
    async def list_by_service(self, service_id: UUID) -> list[CustomField]:
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID, service_id: UUID) -> CustomField | None:
        ...

    @abstractmethod
    async def create(self, entity: CustomField) -> CustomField:
        ...

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        ...
