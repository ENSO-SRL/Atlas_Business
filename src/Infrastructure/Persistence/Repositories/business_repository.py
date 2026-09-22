from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, inspect
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.business import Business, BusinessSchedule
from src.Domain.Enums.platform import Platform
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Enums.weekday import Weekday
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Infrastructure.Persistence.Models.business_model import BusinessModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BusinessRepository(BaseRepository, IBusinessRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BusinessModel) -> Business:
        # Convertir la lista de dicts JSONB a objetos BusinessSchedule
        schedules = [
            BusinessSchedule(
                weekday=Weekday(s["weekday"]),
                opening_time=s["opening_time"],
                closing_time=s["closing_time"],
            )
            for s in (model.schedules or [])
        ]
        category_name = None
        unloaded = inspect(model).unloaded
        if "category" not in unloaded and model.category:
            category_name = model.category.name

        return Business(
            id=model.id,
            code=model.code,
            name=model.name,
            rnc=model.rnc,
            category_id=model.category_id,
            category_name=category_name,
            platform=Platform(model.platform),
            verification_status=VerificationStatus(model.verification_status),
            address=model.address,
            maps_url=model.maps_url,
            phone=model.phone,
            aliases=model.aliases or [],
            schedules=schedules,
            agent_metadata_id=model.agent_metadata_id,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    @staticmethod
    def _schedules_to_json(schedules: list[BusinessSchedule]) -> list[dict]:
        return [
            {
                "weekday": s.weekday.value,
                "opening_time": s.opening_time if isinstance(s.opening_time, str) else s.opening_time.strftime("%H:%M"),
                "closing_time": s.closing_time if isinstance(s.closing_time, str) else s.closing_time.strftime("%H:%M"),
            }
            for s in schedules
        ]

    async def get_by_id(self, id: UUID) -> Business | None:
        stmt = (
            select(BusinessModel)
            .options(joinedload(BusinessModel.category))
            .where(BusinessModel.id == id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Business | None:
        stmt = (
            select(BusinessModel)
            .options(joinedload(BusinessModel.category))
            .where(BusinessModel.code == code)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(self, entity: Business) -> Business:
        model = BusinessModel(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            rnc=entity.rnc,
            category_id=entity.category_id,
            platform=entity.platform.value,
            verification_status=entity.verification_status.value,
            address=entity.address,
            maps_url=entity.maps_url,
            phone=entity.phone,
            aliases=entity.aliases,
            schedules=self._schedules_to_json(entity.schedules),
            agent_metadata_id=entity.agent_metadata_id,
            created_at=entity.created_at,
            created_by=entity.created_by,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def update(self, entity: Business) -> Business:
        stmt = (
            sa.update(BusinessModel)
            .where(BusinessModel.id == entity.id)
            .values(
                name=entity.name,
                phone=entity.phone,
                address=entity.address,
                maps_url=entity.maps_url,
                aliases=entity.aliases,
                schedules=self._schedules_to_json(entity.schedules),
                verification_status=entity.verification_status.value,
                updated_at=entity.updated_at,
                updated_by=entity.updated_by,
            )
        )
        await self.session.execute(stmt)
        return entity
