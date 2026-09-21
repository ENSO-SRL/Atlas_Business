from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.business_user import BusinessUser


class IBusinessUserRepository(ABC):
    @abstractmethod
    async def list_by_business(self, business_id: UUID) -> list[BusinessUser]:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[BusinessUser]:
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID, business_id: UUID) -> BusinessUser | None:
        ...

    @abstractmethod
    async def get_by_user_and_business(self, user_id: UUID, business_id: UUID) -> BusinessUser | None:
        ...

    @abstractmethod
    async def create(self, entity: BusinessUser) -> BusinessUser:
        ...

    @abstractmethod
    async def update(self, entity: BusinessUser) -> BusinessUser:
        ...
