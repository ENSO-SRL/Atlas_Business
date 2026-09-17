from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.service import Service
from src.Domain.Enums.publication_status import PublicationStatus


class IServiceRepository(ABC):
    @abstractmethod
    async def list_by_business(
        self,
        business_id: UUID,
        publication_status: PublicationStatus | None = None,
    ) -> list[Service]:
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID, business_id: UUID) -> Service | None:
        ...

    @abstractmethod
    async def create(self, entity: Service) -> Service:
        ...

    @abstractmethod
    async def update(self, entity: Service) -> Service:
        ...
