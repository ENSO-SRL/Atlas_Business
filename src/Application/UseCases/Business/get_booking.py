from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BookingNotFoundError
from src.Application.UseCases.Business.list_business_bookings import BookingSummaryResult
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository


@dataclass
class GetBookingCommand:
    booking_id: UUID
    business_id: UUID


class GetBookingUseCase:
    """
    Obtiene el detalle completo de una reserva.
    """

    def __init__(self, booking_repo: IBookingRepository):
        self.booking_repo = booking_repo

    async def execute(self, command: GetBookingCommand) -> BookingSummaryResult:
        b = await self.booking_repo.get_by_id(command.booking_id, command.business_id)
        if not b:
            raise BookingNotFoundError()

        service_name = b.service.name if b.service else "Desconocido"
        object_name = b.bookable_object.name if b.bookable_object else None

        return BookingSummaryResult(
            id=b.id,
            service_id=b.service_id,
            service_name=service_name,
            bookable_object_id=b.bookable_object_id,
            bookable_object_name=object_name,
            start_time=b.start_time.isoformat(),
            end_time=b.end_time.isoformat(),
            party_size=b.party_size,
            calculated_amount=str(b.calculated_amount) if b.calculated_amount is not None else None,
            custom_fields=b.custom_fields,
            created_at=b.created_at.isoformat() if b.created_at else None,
        )
