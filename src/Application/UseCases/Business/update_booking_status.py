from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BookingNotFoundError, InvalidBookingStateTransitionError
from src.Domain.Enums.booking_status import BookingStatus
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository


@dataclass
class UpdateBookingStatusCommand:
    booking_id: UUID
    business_id: UUID
    actor_id: UUID
    target_status: BookingStatus


class UpdateBookingStatusUseCase:
    """
    Máquina de estados estricta para el ciclo de vida de una reserva.
    """

    def __init__(self, booking_repo: IBookingRepository):
        self.booking_repo = booking_repo

    async def execute(self, command: UpdateBookingStatusCommand) -> None:
        booking = await self.booking_repo.get_by_id(command.booking_id, command.business_id)
        if not booking:
            raise BookingNotFoundError()

        current = booking.status
        target = command.target_status

        if current == target:
            return  # No-op

        # Reglas de transición de la máquina de estados
        valid_transition = False
        
        if target == BookingStatus.APPROVED:
            if current == BookingStatus.REQUESTED:
                valid_transition = True
                
        elif target == BookingStatus.REJECTED:
            if current == BookingStatus.REQUESTED:
                valid_transition = True
                
        elif target == BookingStatus.CONFIRMED:
            if current == BookingStatus.APPROVED:
                valid_transition = True
                
        elif target == BookingStatus.CANCELLED:
            if current in (BookingStatus.REQUESTED, BookingStatus.APPROVED):
                valid_transition = True

        if not valid_transition:
            raise InvalidBookingStateTransitionError(current, target)

        booking.status = target
        booking.updated_at = datetime.now(timezone.utc)
        booking.updated_by = command.actor_id

        await self.booking_repo.update(booking)
