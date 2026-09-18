from datetime import datetime, timezone
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.booking import Booking
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository, OccupiedGroup
from src.Infrastructure.Persistence.Models.booking_model import BookingModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository
from src.Infrastructure.Persistence.Repositories.exceptions import SlotAlreadyBookedInfraError


class ClientBookingRepository(BaseRepository, IClientBookingRepository):
    """
    Repositorio de reservas para la Client API.
    Contiene queries optimizados para el algoritmo de disponibilidad de slots.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_occupied_groups(
        self,
        object_ids: list[UUID],
        day_start: datetime,
        day_end: datetime,
    ) -> list[OccupiedGroup]:
        """
        Query agrupado que colapsa reservas por (start_time, end_time).
        Utiliza el índice ix_booking_object_start sobre (bookable_object_id, start_time).
        """
        if not object_ids:
            return []

        stmt = (
            select(
                BookingModel.start_time,
                BookingModel.end_time,
                func.count().label("count"),
            )
            .where(
                BookingModel.bookable_object_id.in_(object_ids),
                BookingModel.start_time < day_end,
                BookingModel.end_time > day_start,
            )
            .group_by(BookingModel.start_time, BookingModel.end_time)
        )

        rows = (await self.session.execute(stmt)).all()
        return [
            OccupiedGroup(
                start_time=r.start_time,
                end_time=r.end_time,
                count=r.count,
            )
            for r in rows
        ]

    async def get_occupied_object_ids(
        self,
        object_ids: list[UUID],
        slot_start: datetime,
        slot_end: datetime,
    ) -> set[UUID]:
        """
        Devuelve los IDs de objetos específicos ocupados en [slot_start, slot_end).
        """
        if not object_ids:
            return set()

        stmt = (
            select(distinct(BookingModel.bookable_object_id))
            .where(
                BookingModel.bookable_object_id.in_(object_ids),
                BookingModel.start_time < slot_end,
                BookingModel.end_time > slot_start,
            )
        )

        rows = (await self.session.execute(stmt)).scalars().all()
        return set(rows)

    async def create(self, entity: Booking) -> Booking:
        model = BookingModel(
            id=entity.id,
            service_id=entity.service_id,
            bookable_object_id=entity.bookable_object_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
            party_size=entity.party_size,
            calculated_amount=entity.calculated_amount,
            custom_fields=entity.custom_fields,
            created_at=entity.created_at or datetime.now(timezone.utc),
            created_by=entity.created_by,
        )
        self.session.add(model)

        try:
            await self.session.flush()
        except Exception as exc:
            # asyncpg lanza ExclusionViolationError cuando el constraint GiST es violado.
            # Lo capturamos por el nombre del tipo para evitar importar asyncpg directamente.
            if "ExclusionViolationError" in type(exc).__name__:
                raise SlotAlreadyBookedInfraError() from exc
            raise

        return entity
