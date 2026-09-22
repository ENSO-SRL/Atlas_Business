from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.business_category import BusinessCategory
from src.Domain.Ports.Repositories.i_business_category_repository import IBusinessCategoryRepository
from src.Infrastructure.Persistence.Models.business_category_model import BusinessCategoryModel


class BusinessCategoryRepository(IBusinessCategoryRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _to_entity(model: BusinessCategoryModel) -> BusinessCategory:
        return BusinessCategory(
            id=model.id,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            is_deleted=model.is_deleted,
        )

    async def create(self, entity: BusinessCategory) -> BusinessCategory:
        model = BusinessCategoryModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            is_deleted=entity.is_deleted,
        )
        self._session.add(model)
        await self._session.flush()
        return entity

    async def get_by_id(self, id: UUID) -> BusinessCategory | None:
        stmt = select(BusinessCategoryModel).where(
            BusinessCategoryModel.id == id,
            BusinessCategoryModel.is_deleted == False,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, only_active: bool = True) -> list[BusinessCategory]:
        stmt = select(BusinessCategoryModel).where(BusinessCategoryModel.is_deleted == False)
        if only_active:
            stmt = stmt.where(BusinessCategoryModel.is_active == True)
        stmt = stmt.order_by(BusinessCategoryModel.name)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: BusinessCategory) -> BusinessCategory:
        stmt = (
            sa.update(BusinessCategoryModel)
            .where(BusinessCategoryModel.id == entity.id)
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
