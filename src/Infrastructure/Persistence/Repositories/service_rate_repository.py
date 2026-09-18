from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.service_rate import ServiceRate
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Infrastructure.Persistence.Models.service_rate_model import ServiceRateModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class ServiceRateRepository(BaseRepository, IServiceRateRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: ServiceRateModel) -> ServiceRate:
        return ServiceRate(
            id=model.id,
            service_id=model.service_id,
            weekdays=model.weekdays or [],
            start_time=model.start_time,
            end_time=model.end_time,
            amount=model.amount,
            calculation_basis=CalculationBasis(model.calculation_basis),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )

    async def list_by_service(self, service_id: UUID) -> list[ServiceRate]:
        stmt = select(ServiceRateModel).where(ServiceRateModel.service_id == service_id)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def replace_all(self, service_id: UUID, new_rates: list[ServiceRate]) -> list[ServiceRate]:
        # 1. Eliminar todas las tarifas existentes del servicio
        await self.session.execute(
            sa.delete(ServiceRateModel).where(ServiceRateModel.service_id == service_id)
        )

        # 2. Insertar el nuevo conjunto de tarifas
        new_models = [
            ServiceRateModel(
                id=r.id,
                service_id=r.service_id,
                weekdays=r.weekdays,
                start_time=r.start_time,
                end_time=r.end_time,
                amount=r.amount,
                calculation_basis=r.calculation_basis.value,
                created_at=r.created_at,
                created_by=r.created_by,
            )
            for r in new_rates
        ]
        self.session.add_all(new_models)
        await self.session.flush()

        return new_rates
