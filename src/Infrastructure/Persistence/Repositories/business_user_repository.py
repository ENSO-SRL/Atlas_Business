from sqlalchemy.orm import selectinload
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, inspect, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Entities.user import User
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Infrastructure.Persistence.Models.business_user_model import BusinessUserModel
from src.Infrastructure.Persistence.Models.user_model import UserModel
from src.Infrastructure.Persistence.Models.business_model import BusinessModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BusinessUserRepository(BaseRepository, IBusinessUserRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BusinessUserModel) -> BusinessUser:
        user_entity = None
        unloaded = inspect(model).unloaded

        if "user" not in unloaded and model.user:
            user_entity = User(
                id=model.user.id,
                first_name=model.user.first_name,
                last_name=model.user.last_name,
                email=model.user.email,
                phone=model.user.phone,
                hashed_password=model.user.hashed_password,
                is_active=model.user.is_active,
                created_at=model.user.created_at,
                updated_at=model.user.updated_at,
            )
            
        business_name = None
        business_code = None
        if "business" not in unloaded and model.business:
            business_name = model.business.name
            business_code = model.business.code

        return BusinessUser(
            id=model.id,
            user_id=model.user_id,
            business_id=model.business_id,
            roles=[SystemRole(r) for r in (model.roles or [])],
            is_active=model.is_active,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            user=user_entity,
            business_name=business_name,
            business_code=business_code,
        )

    async def list_by_business(self, business_id: UUID) -> list[BusinessUser]:
        stmt = (
            select(BusinessUserModel)
            .options(joinedload(BusinessUserModel.user))
            .where(BusinessUserModel.business_id == business_id)
        )
        # Order by requiere join si es por nombre del usuario
        stmt = stmt.join(BusinessUserModel.user).order_by(UserModel.first_name)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_user(self, user_id: UUID) -> list[BusinessUser]:
        stmt = (
            select(BusinessUserModel)
            .options(joinedload(BusinessUserModel.business))
            .where(BusinessUserModel.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_paginated_by_user(self, user_id: UUID, page: int, page_size: int) -> tuple[list[BusinessUser], int]:
        base_stmt = select(BusinessUserModel).where(BusinessUserModel.user_id == user_id)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one_or_none() or 0

        stmt = (
            base_stmt
            .options(joinedload(BusinessUserModel.business))
            .order_by(BusinessUserModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()], total

    async def get_by_id(self, id: UUID, business_id: UUID) -> BusinessUser | None:
        stmt = (
            select(BusinessUserModel)
            .options(joinedload(BusinessUserModel.user))
            .where(
                BusinessUserModel.id == id,
                BusinessUserModel.business_id == business_id,
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_business(self, user_id: UUID, business_id: UUID) -> BusinessUser | None:
        stmt = (
            select(BusinessUserModel)
            .options(
                joinedload(BusinessUserModel.user),
                joinedload(BusinessUserModel.business)
            )
            .where(
                BusinessUserModel.user_id == user_id,
                BusinessUserModel.business_id == business_id,
                BusinessUserModel.is_active == True,
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: BusinessUser) -> BusinessUser:
        model = BusinessUserModel(
            id=entity.id,
            user_id=entity.user_id,
            business_id=entity.business_id,
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
