from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.bookable_object import BookableObject
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Infrastructure.Persistence.Models.bookable_object_model import BookableObjectModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BookableObjectRepository(BaseRepository, IBookableObjectRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BookableObjectModel) -> BookableObject:
        return BookableObject(
            id=model.id,
            service_id=model.service_id,
            name=model.name,
            min_capacity=model.min_capacity,
            max_capacity=model.max_capacity,
            is_active=model.is_active,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def list_by_service(self, service_id: UUID) -> list[BookableObject]:
        stmt = (
            select(BookableObjectModel)
            .where(BookableObjectModel.service_id == service_id)
            .order_by(BookableObjectModel.name.nullslast())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, id: UUID, service_id: UUID) -> BookableObject | None:
        stmt = select(BookableObjectModel).where(
            BookableObjectModel.id == id,
            BookableObjectModel.service_id == service_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: BookableObject) -> BookableObject:
        model = BookableObjectModel(
            id=entity.id,
            service_id=entity.service_id,
            name=entity.name,
            min_capacity=entity.min_capacity,
            max_capacity=entity.max_capacity,
            is_active=entity.is_active,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: BookableObject) -> BookableObject:
        stmt = (
            sa.update(BookableObjectModel)
            .where(BookableObjectModel.id == entity.id)
            .values(
                name=entity.name,
                min_capacity=entity.min_capacity,
                max_capacity=entity.max_capacity,
                is_active=entity.is_active,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
