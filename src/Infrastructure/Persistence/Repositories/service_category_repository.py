from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.service_category import ServiceCategory
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Infrastructure.Persistence.Models.service_category_model import ServiceCategoryModel


class ServiceCategoryRepository(IServiceCategoryRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _to_entity(model: ServiceCategoryModel) -> ServiceCategory:
        return ServiceCategory(
            id=model.id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            is_deleted=model.is_deleted,
        )

    async def create(self, entity: ServiceCategory) -> ServiceCategory:
        model = ServiceCategoryModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            is_deleted=entity.is_deleted,
        )
        self._session.add(model)
        await self._session.flush()
        return entity

    async def get_by_id(self, id: UUID) -> ServiceCategory | None:
        stmt = select(ServiceCategoryModel).where(
            ServiceCategoryModel.id == id,
            ServiceCategoryModel.is_deleted == False,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, only_active: bool = True) -> list[ServiceCategory]:
        stmt = select(ServiceCategoryModel).where(ServiceCategoryModel.is_deleted == False)
        if only_active:
            stmt = stmt.where(ServiceCategoryModel.is_active == True)
        stmt = stmt.order_by(ServiceCategoryModel.name)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: ServiceCategory) -> ServiceCategory:
        stmt = (
            sa.update(ServiceCategoryModel)
            .where(ServiceCategoryModel.id == entity.id)
            .values(
                name=entity.name,
                description=entity.description,
                is_active=entity.is_active,
                is_deleted=entity.is_deleted,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()
        return entity
