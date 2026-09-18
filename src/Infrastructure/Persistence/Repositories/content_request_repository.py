from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.content_request import ContentRequest, ContentRequestStatus
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Infrastructure.Persistence.Models.content_request_model import ContentRequestModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class ContentRequestRepository(BaseRepository, IContentRequestRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: ContentRequestModel) -> ContentRequest:
        return ContentRequest(
            id=model.id,
            service_id=model.service_id,
            status=ContentRequestStatus(model.status),
            payload=model.payload or {},
            filter_matches=model.filter_matches or [],
            rejection_reason=model.rejection_reason,
            reviewed_by=model.reviewed_by,
            reviewed_at=model.reviewed_at,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def get_active_by_service(self, service_id: UUID) -> ContentRequest | None:
        """
        Aprovecha el partial index ix_content_request_active sobre status IN ('PENDING_FILTER', 'UNDER_REVIEW').
        En la práctica devuelve 0 o 1 fila.
        """
        stmt = select(ContentRequestModel).where(
            ContentRequestModel.service_id == service_id,
            ContentRequestModel.status.in_(["PENDING_FILTER", "UNDER_REVIEW"]),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: ContentRequest) -> ContentRequest:
        model = ContentRequestModel(
            id=entity.id,
            service_id=entity.service_id,
            status=entity.status.value,
            payload=entity.payload,
            filter_matches=entity.filter_matches,
            rejection_reason=entity.rejection_reason,
            reviewed_by=entity.reviewed_by,
            reviewed_at=entity.reviewed_at,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: ContentRequest) -> ContentRequest:
        stmt = (
            sa.update(ContentRequestModel)
            .where(ContentRequestModel.id == entity.id)
            .values(
                status=entity.status.value,
                rejection_reason=entity.rejection_reason,
                reviewed_by=entity.reviewed_by,
                reviewed_at=entity.reviewed_at,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
