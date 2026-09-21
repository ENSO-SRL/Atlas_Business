from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def create(self, entity: User) -> User:
        ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        ...
