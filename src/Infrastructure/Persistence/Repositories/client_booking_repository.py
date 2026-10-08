from datetime import datetime, timezone
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.booking import Booking
from src.Domain.Enums.booking_status import BookingStatus
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
                BookingModel.status.in_([
                    BookingStatus.REQUESTED.value,
                    BookingStatus.APPROVED.value,
                    BookingStatus.CONFIRMED.value
                ])
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
                BookingModel.status.in_([
                    BookingStatus.REQUESTED.value,
                    BookingStatus.APPROVED.value,
                    BookingStatus.CONFIRMED.value
                ])
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
            status=entity.status.value,
            customer_id=entity.customer_id,
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

    async def count_active_bookings_by_customer(
        self,
        service_id: UUID,
        customer_id: UUID,
        target_date: datetime.date,
    ) -> int:
        day_start = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        stmt = (
            select(func.count())
            .select_from(BookingModel)
            .where(
                BookingModel.service_id == service_id,
                BookingModel.customer_id == customer_id,
                BookingModel.start_time >= day_start,
                BookingModel.start_time <= day_end,
                BookingModel.status.in_([
                    BookingStatus.REQUESTED.value,
                    BookingStatus.APPROVED.value,
                    BookingStatus.CONFIRMED.value
                ])
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
