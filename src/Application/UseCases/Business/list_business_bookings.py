from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository


@dataclass
class ListBusinessBookingsCommand:
    business_id: UUID
    service_id: UUID | None = None
    filter_date: date | None = None
    page: int = 1
    page_size: int = 20


@dataclass
class BookingSummaryResult:
    id: UUID
    service_id: UUID
    service_name: str
    bookable_object_id: UUID
    bookable_object_name: str | None
    start_time: str
    end_time: str
    party_size: int
    calculated_amount: str | None
    custom_fields: dict
    created_at: str | None


@dataclass
class PaginatedBookingResult:
    items: list[BookingSummaryResult]
    total: int
    page: int
    page_size: int


class ListBusinessBookingsUseCase:
    """
    Lista las reservas de un negocio, con soporte para paginación y filtros opcionales por servicio y fecha.
    """

    def __init__(self, booking_repo: IBookingRepository):
        self.booking_repo = booking_repo

    async def execute(self, command: ListBusinessBookingsCommand) -> PaginatedBookingResult:
        bookings, total = await self.booking_repo.list_by_business(
            business_id=command.business_id,
            service_id=command.service_id,
            filter_date=command.filter_date,
            page=command.page,
            page_size=command.page_size,
        )

        items = []
        for b in bookings:
            # Dado que el repositorio de lectura puede hacer JOIN (eager load), 
            # asumimos que service y bookable_object están cargados si es necesario para el DTO.
            # (El puerto debe ser implementado para cargar name del servicio y del objeto)
            service_name = b.service.name if b.service else "Desconocido"
            object_name = b.bookable_object.name if b.bookable_object else None

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
                    created_at=b.created_at.isoformat() if b.created_at else None,
                )
            )

        return PaginatedBookingResult(
            items=items,
            total=total,
            page=command.page,
            page_size=command.page_size,
        )
