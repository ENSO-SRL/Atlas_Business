from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.business_customer import BusinessCustomer
from src.Domain.Enums.gender import Gender
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository
from src.Infrastructure.Persistence.Models.business_customer_model import BusinessCustomerModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BusinessCustomerRepository(BaseRepository, IBusinessCustomerRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BusinessCustomerModel) -> BusinessCustomer:
        return BusinessCustomer(
            id=model.id,
            business_id=model.business_id,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            email=model.email,
            gender=Gender(model.gender) if model.gender else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: BusinessCustomer) -> BusinessCustomerModel:
        return BusinessCustomerModel(
            id=entity.id,
            business_id=entity.business_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            email=entity.email,
            gender=entity.gender.value if entity.gender else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID, business_id: UUID) -> BusinessCustomer | None:
        stmt = select(BusinessCustomerModel).where(
            BusinessCustomerModel.id == id,
            BusinessCustomerModel.business_id == business_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_phone(self, phone: str, business_id: UUID) -> BusinessCustomer | None:
        stmt = select(BusinessCustomerModel).where(
            BusinessCustomerModel.phone == phone,
            BusinessCustomerModel.business_id == business_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_paginated_by_business(
        self, business_id: UUID, page: int, page_size: int
    ) -> tuple[list[BusinessCustomer], int]:
        
        base_stmt = select(BusinessCustomerModel).where(BusinessCustomerModel.business_id == business_id)
        
        # Total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Paginated items
        stmt = base_stmt.order_by(BusinessCustomerModel.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items_result = await self.session.execute(stmt)
        models = items_result.scalars().all()
        
        return [self._to_entity(m) for m in models], total

    async def create(self, entity: BusinessCustomer) -> BusinessCustomer:
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def update(self, entity: BusinessCustomer) -> BusinessCustomer:
        stmt = select(BusinessCustomerModel).where(
            BusinessCustomerModel.id == entity.id,
            BusinessCustomerModel.business_id == entity.business_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.first_name = entity.first_name
            model.last_name = entity.last_name
            model.phone = entity.phone
            model.email = entity.email
            model.gender = entity.gender.value if entity.gender else None
            model.updated_at = entity.updated_at
            
        await self.session.flush()
        return entity
