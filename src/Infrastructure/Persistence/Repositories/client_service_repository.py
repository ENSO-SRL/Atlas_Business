from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.service import Service
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Infrastructure.Persistence.Models.service_model import ServiceModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository
from src.Infrastructure.Persistence.Repositories.service_repository import ServiceRepository


class ClientServiceRepository(BaseRepository, IClientServiceRepository):
    """
    Repositorio de servicios para la Client API.
    Siempre filtra por publication_status = 'PUBLISHED'.
    Reutiliza el método _to_entity de ServiceRepository.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_published_by_id(self, service_id: UUID, business_id: UUID) -> Service | None:
        stmt = select(ServiceModel).where(
            ServiceModel.id == service_id,
            ServiceModel.business_id == business_id,
            ServiceModel.publication_status == "PUBLISHED",
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return ServiceRepository._to_entity(model) if model else None

    async def get_published_by_id_only(self, service_id: UUID) -> Service | None:
        stmt = select(ServiceModel).where(
            ServiceModel.id == service_id,
            ServiceModel.publication_status == "PUBLISHED",
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return ServiceRepository._to_entity(model) if model else None

    async def list_published_by_business(self, business_id: UUID) -> list[Service]:
        stmt = (
            select(ServiceModel)
            .where(
                ServiceModel.business_id == business_id,
                ServiceModel.publication_status == "PUBLISHED",
            )
            .order_by(ServiceModel.name)
        )
        result = await self.session.execute(stmt)
        return [ServiceRepository._to_entity(m) for m in result.scalars().all()]
