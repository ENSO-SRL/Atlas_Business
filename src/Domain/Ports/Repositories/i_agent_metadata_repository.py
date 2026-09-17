from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.agent_metadata import AgentMetadata


class IAgentMetadataRepository(ABC):
    @abstractmethod
    async def create(self, entity: AgentMetadata) -> AgentMetadata:
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> AgentMetadata | None:
        ...

    @abstractmethod
    async def update(self, entity: AgentMetadata) -> AgentMetadata:
        ...
