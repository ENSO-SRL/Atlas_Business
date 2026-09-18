from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.custom_field import CustomField
from src.Domain.Enums.data_type import DataType
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Infrastructure.Persistence.Models.custom_field_model import CustomFieldModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class CustomFieldRepository(BaseRepository, ICustomFieldRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: CustomFieldModel) -> CustomField:
        return CustomField(
            id=model.id,
            business_id=model.business_id,
            service_id=model.service_id,
            label=model.label,
            agent_note=model.agent_note,
            order=model.order,
            required=model.required,
            visible_to_client=model.visible_to_client,
            data_type=DataType(model.data_type),
            options=model.options,
            minimum=model.minimum,
            maximum=model.maximum,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def list_by_service(self, service_id: UUID) -> list[CustomField]:
        stmt = (
            select(CustomFieldModel)
            .where(CustomFieldModel.service_id == service_id)
            .order_by(CustomFieldModel.order)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, id: UUID, service_id: UUID) -> CustomField | None:
        stmt = select(CustomFieldModel).where(
            CustomFieldModel.id == id,
            CustomFieldModel.service_id == service_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: CustomField) -> CustomField:
        model = CustomFieldModel(
            id=entity.id,
            business_id=entity.business_id,
            service_id=entity.service_id,
            label=entity.label,
            agent_note=entity.agent_note,
            order=entity.order,
            required=entity.required,
            visible_to_client=entity.visible_to_client,
            data_type=entity.data_type.value,
            options=entity.options,
            minimum=entity.minimum,
            maximum=entity.maximum,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def delete(self, id: UUID) -> None:
        await self.session.execute(
            sa.delete(CustomFieldModel).where(CustomFieldModel.id == id)
        )
