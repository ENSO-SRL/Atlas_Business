from datetime import date
from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Business.get_booking import GetBookingCommand, GetBookingUseCase
from src.Application.UseCases.Business.list_business_bookings import ListBusinessBookingsCommand, ListBusinessBookingsUseCase
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository
from src.Presentation.Dependencies.auth import UserContext, get_current_user
from src.Presentation.Dependencies.repositories import get_booking_repo

router = APIRouter()


@router.get("/")
async def list_business_bookings(
    service_id: UUID | None = None,
    filter_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
    user: UserContext = Depends(get_current_user),
    booking_repo: IBookingRepository = Depends(get_booking_repo),
):
    use_case = ListBusinessBookingsUseCase(booking_repo)
    command = ListBusinessBookingsCommand(
        business_id=user.business_id,
        service_id=service_id,
        filter_date=filter_date,
        page=page,
        page_size=page_size,
    )
    result = await use_case.execute(command)
    return {
        "items": result.items,
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
    }


@router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    user: UserContext = Depends(get_current_user),
    booking_repo: IBookingRepository = Depends(get_booking_repo),
):
    use_case = GetBookingUseCase(booking_repo)
    command = GetBookingCommand(
        business_id=user.business_id,
        booking_id=booking_id,
    )
    result = await use_case.execute(command)
    return result
