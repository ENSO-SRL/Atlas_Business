from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.Domain.Entities.booking import Booking
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository
from src.Infrastructure.Persistence.Models.booking_model import BookingModel
from src.Infrastructure.Persistence.Models.service_model import ServiceModel
from src.Infrastructure.Persistence.Repositories.base_repository import BaseRepository


class BookingRepository(BaseRepository, IBookingRepository):
    """
    Repositorio de reservas para la Business API.
    Nota: la tabla booking no tiene business_id directamente — se llega via service.business_id.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _to_entity(model: BookingModel) -> Booking:
        # Adjuntar datos de relaciones ORM al objeto para que el UC los pueda usar
        booking = Booking(
            id=model.id,
            service_id=model.service_id,
            bookable_object_id=model.bookable_object_id,
            start_time=model.start_time,
            end_time=model.end_time,
            party_size=model.party_size,
            calculated_amount=model.calculated_amount,
            customer_id=model.customer_id,
            custom_fields=model.custom_fields or {},
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )
        # Adjuntar relaciones cargadas como atributos temporales para el UC
        booking.service = model.service  # type: ignore[attr-defined]
        booking.bookable_object = model.bookable_object  # type: ignore[attr-defined]
        return booking

    def _base_stmt(self, business_id: UUID, service_id: UUID | None, filter_date: date | None):
        stmt = (
            select(BookingModel)
            .join(ServiceModel, BookingModel.service_id == ServiceModel.id)
            .options(
                joinedload(BookingModel.service),
                joinedload(BookingModel.bookable_object),
            )
            .where(ServiceModel.business_id == business_id)
        )
        if service_id is not None:
            stmt = stmt.where(BookingModel.service_id == service_id)
        if filter_date is not None:
            stmt = stmt.where(sa.cast(BookingModel.start_time, sa.Date) == filter_date)
        return stmt

    async def list_by_business(
        self,
        business_id: UUID,
        service_id: UUID | None = None,
        filter_date: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Booking], int]:
        base = self._base_stmt(business_id, service_id, filter_date)

        # Total count
        count_stmt = (
            select(func.count())
            .select_from(BookingModel)
            .join(ServiceModel, BookingModel.service_id == ServiceModel.id)
            .where(ServiceModel.business_id == business_id)
        )
        if service_id is not None:
            count_stmt = count_stmt.where(BookingModel.service_id == service_id)
        if filter_date is not None:
            count_stmt = count_stmt.where(
                sa.cast(BookingModel.start_time, sa.Date) == filter_date
            )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        paged_stmt = base.order_by(BookingModel.start_time.desc()).limit(page_size).offset(offset)
        result = await self.session.execute(paged_stmt)
        items = [self._to_entity(m) for m in result.unique().scalars().all()]

        return items, total

    async def get_by_id(self, id: UUID, business_id: UUID) -> Booking | None:
        stmt = (
            select(BookingModel)
            .join(ServiceModel, BookingModel.service_id == ServiceModel.id)
            .options(
                joinedload(BookingModel.service),
                joinedload(BookingModel.bookable_object),
            )
            .where(
                BookingModel.id == id,
                ServiceModel.business_id == business_id,
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_customer(
        self,
        customer_id: UUID,
        business_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Booking], int]:
        base_stmt = (
            select(BookingModel)
            .join(ServiceModel, BookingModel.service_id == ServiceModel.id)
            .options(
                joinedload(BookingModel.service),
                joinedload(BookingModel.bookable_object),
            )
            .where(
                BookingModel.customer_id == customer_id,
                ServiceModel.business_id == business_id
            )
        )
        
        count_stmt = (
            select(func.count())
            .select_from(BookingModel)
            .join(ServiceModel, BookingModel.service_id == ServiceModel.id)
            .where(
                BookingModel.customer_id == customer_id,
                ServiceModel.business_id == business_id
            )
        )
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        paged_stmt = base_stmt.order_by(BookingModel.start_time.desc()).limit(page_size).offset(offset)
        result = await self.session.execute(paged_stmt)
        items = [self._to_entity(m) for m in result.unique().scalars().all()]

        return items, total
