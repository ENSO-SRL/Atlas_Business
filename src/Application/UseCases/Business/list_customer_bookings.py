from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository


@dataclass
class ListCustomerBookingsCommand:
    business_id: UUID
    customer_id: UUID
    page: int
    page_size: int


@dataclass
class CustomerBookingResult:
    id: UUID
    service_id: UUID
    service_name: str
    bookable_object_name: str
    start_time: str
    end_time: str
    party_size: int
    calculated_amount: str | None
    created_at: str | None


class ListCustomerBookingsUseCase:
    def __init__(self, booking_repo: IBookingRepository):
        self.booking_repo = booking_repo

    async def execute(self, command: ListCustomerBookingsCommand) -> tuple[list[CustomerBookingResult], int]:
        bookings, total = await self.booking_repo.list_by_customer(
            customer_id=command.customer_id,
            business_id=command.business_id,
            page=command.page,
            page_size=command.page_size,
        )

        results = [
            CustomerBookingResult(
                id=b.id,
                service_id=b.service_id,
                service_name=b.service.name if hasattr(b, 'service') and b.service else "Unknown",
                bookable_object_name=b.bookable_object.name if hasattr(b, 'bookable_object') and b.bookable_object and b.bookable_object.name else "Object",
                start_time=b.start_time.isoformat(),
                end_time=b.end_time.isoformat(),
                party_size=b.party_size,
                calculated_amount=str(b.calculated_amount) if b.calculated_amount is not None else None,
                created_at=b.created_at.isoformat() if b.created_at else None,
            )
            for b in bookings
        ]

        return results, total
