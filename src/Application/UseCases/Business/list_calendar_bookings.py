from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.Application.UseCases.Business.list_business_bookings import BookingSummaryResult, CustomerSummary
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository


@dataclass
class ListCalendarBookingsCommand:
    business_id: UUID
    date_from: date
    date_to: date
    service_id: UUID | None = None


class ListCalendarBookingsUseCase:
    """
    Lista las reservas de un negocio sin paginar, exclusivamente para alimentar la vista de un calendario.
    Exige rango de fechas para evitar sobrecarga de la BD.
    """

    def __init__(self, booking_repo: IBookingRepository):
        self.booking_repo = booking_repo

    async def execute(self, command: ListCalendarBookingsCommand) -> list[BookingSummaryResult]:
        bookings = await self.booking_repo.list_for_calendar(
            business_id=command.business_id,
            date_from=command.date_from,
            date_to=command.date_to,
            service_id=command.service_id,
        )

        items = []
        for b in bookings:
            service_name = b.service.name if b.service else "Desconocido"
            object_name = b.bookable_object.name if b.bookable_object else None

            customer_summary = None
            if b.customer:
                customer_summary = CustomerSummary(
                    id=b.customer.id,
                    full_name=f"{b.customer.first_name} {b.customer.last_name}".strip(),
                    phone=b.customer.phone,
                )

            items.append(
                BookingSummaryResult(
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
                    status=b.status.value,
                    customer=customer_summary,
                    created_at=b.created_at.isoformat() if b.created_at else None,
                )
            )

        return items
