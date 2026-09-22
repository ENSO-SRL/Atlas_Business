from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.service import Service, DurationNature, BillingNature, AutoSelectionCriteria
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Infrastructure.Persistence.Models.service_model import ServiceModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository, IServiceRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: ServiceModel) -> Service:
        return Service(
            id=model.id,
            business_id=model.business_id,
            name=model.name,
            occupation_duration_minutes=model.occupation_duration_minutes,
            duration_nature=DurationNature(model.duration_nature),
            exposes_end_time=model.exposes_end_time,
            buffer_minutes=model.buffer_minutes,
            grid_interval_minutes=model.grid_interval_minutes,
            allows_manual_object_selection=model.allows_manual_object_selection,
            auto_selection_criteria=AutoSelectionCriteria(model.auto_selection_criteria),
            billing_nature=BillingNature(model.billing_nature),
            agent_metadata_id=model.agent_metadata_id,
            category_id=model.category_id,
            publication_status=PublicationStatus(model.publication_status),
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def list_by_business(
        self, business_id: UUID, status: PublicationStatus | None = None
    ) -> list[Service]:
        stmt = select(ServiceModel).where(ServiceModel.business_id == business_id)
        if status is not None:
            stmt = stmt.where(ServiceModel.publication_status == status.value)
        stmt = stmt.order_by(ServiceModel.name)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, id: UUID, business_id: UUID) -> Service | None:
        stmt = select(ServiceModel).where(
            ServiceModel.id == id,
            ServiceModel.business_id == business_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: Service) -> Service:
        model = ServiceModel(
            id=entity.id,
            business_id=entity.business_id,
            name=entity.name,
            occupation_duration_minutes=entity.occupation_duration_minutes,
            duration_nature=entity.duration_nature.value,
            exposes_end_time=entity.exposes_end_time,
            buffer_minutes=entity.buffer_minutes,
            grid_interval_minutes=entity.grid_interval_minutes,
            allows_manual_object_selection=entity.allows_manual_object_selection,
            auto_selection_criteria=entity.auto_selection_criteria.value,
            billing_nature=entity.billing_nature.value,
            agent_metadata_id=entity.agent_metadata_id,
            category_id=entity.category_id,
            publication_status=entity.publication_status.value,
            rejection_reason=entity.rejection_reason,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: Service) -> Service:
        stmt = (
            sa.update(ServiceModel)
            .where(ServiceModel.id == entity.id)
            .values(
                name=entity.name,
                buffer_minutes=entity.buffer_minutes,
                grid_interval_minutes=entity.grid_interval_minutes,
                exposes_end_time=entity.exposes_end_time,
                publication_status=entity.publication_status.value,
                rejection_reason=entity.rejection_reason,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
