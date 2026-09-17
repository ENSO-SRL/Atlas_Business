from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.content_request import ContentRequest


class IContentRequestRepository(ABC):
    @abstractmethod
    async def get_active_by_service(self, service_id: UUID) -> ContentRequest | None:
        """
        "Activa" = status in (PENDING_FILTER, UNDER_REVIEW). Usa el partial index.
        """
        ...

    @abstractmethod
    async def create(self, entity: ContentRequest) -> ContentRequest:
        ...

    @abstractmethod
    async def update(self, entity: ContentRequest) -> ContentRequest:
        ...
