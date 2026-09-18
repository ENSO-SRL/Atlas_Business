from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Infrastructure.Persistence.Models.business_user_model import BusinessUserModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BusinessUserRepository(BaseRepository, IBusinessUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BusinessUserModel) -> BusinessUser:
        return BusinessUser(
            id=model.id,
            business_id=model.business_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            hashed_password=model.hashed_password,
            roles=[SystemRole(r) for r in (model.roles or [])],
            is_active=model.is_active,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def list_by_business(self, business_id: UUID) -> list[BusinessUser]:
        stmt = (
            select(BusinessUserModel)
            .where(BusinessUserModel.business_id == business_id)
            .order_by(BusinessUserModel.first_name)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, id: UUID, business_id: UUID) -> BusinessUser | None:
        stmt = select(BusinessUserModel).where(
            BusinessUserModel.id == id,
            BusinessUserModel.business_id == business_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str, business_id: UUID) -> BusinessUser | None:
        stmt = select(BusinessUserModel).where(
            BusinessUserModel.email == email,
            BusinessUserModel.business_id == business_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: BusinessUser) -> BusinessUser:
        model = BusinessUserModel(
            id=entity.id,
            business_id=entity.business_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            phone=entity.phone,
            hashed_password=entity.hashed_password,
            roles=[r.value for r in entity.roles],
            is_active=entity.is_active,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: BusinessUser) -> BusinessUser:
        stmt = (
            sa.update(BusinessUserModel)
            .where(BusinessUserModel.id == entity.id)
            .values(
                roles=[r.value for r in entity.roles],
                is_active=entity.is_active,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
