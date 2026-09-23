from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.business import Business


class IClientBusinessRepository(ABC):
    @abstractmethod
    async def list_published(self, category_id: UUID | None, page: int, page_size: int) -> tuple[list[Business], int]:
        ...
