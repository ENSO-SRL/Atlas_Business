from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.agent_metadata import AgentMetadata
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Infrastructure.Persistence.Models.agent_metadata_model import AgentMetadataModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class AgentMetadataRepository(BaseRepository, IAgentMetadataRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: AgentMetadataModel) -> AgentMetadata:
        return AgentMetadata(
            id=model.id,
            description=model.description,
            establishment_policies=model.establishment_policies or [],
            pre_booking_requirements=model.pre_booking_requirements or [],
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    @staticmethod
    def _to_model(entity: AgentMetadata) -> AgentMetadataModel:
        return AgentMetadataModel(
            id=entity.id,
            description=entity.description,
            establishment_policies=entity.establishment_policies,
            pre_booking_requirements=entity.pre_booking_requirements,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
        )

    async def get_by_id(self, id: UUID) -> AgentMetadata | None:
        stmt = select(AgentMetadataModel).where(AgentMetadataModel.id == id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: AgentMetadata) -> AgentMetadata:
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: AgentMetadata) -> AgentMetadata:
        stmt = (
            sa.update(AgentMetadataModel)
            .where(AgentMetadataModel.id == entity.id)
            .values(
                description=entity.description,
                establishment_policies=entity.establishment_policies,
                pre_booking_requirements=entity.pre_booking_requirements,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
