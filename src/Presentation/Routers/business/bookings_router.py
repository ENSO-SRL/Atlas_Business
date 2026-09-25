from datetime import date
from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Business.get_booking import GetBookingCommand, GetBookingUseCase
from src.Application.UseCases.Business.list_business_bookings import ListBusinessBookingsCommand, ListBusinessBookingsUseCase
from src.Application.UseCases.Business.create_internal_booking import CreateInternalBookingCommand, CreateInternalBookingUseCase
from src.Domain.Ports.Repositories.i_booking_repository import IBookingRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository
from src.Presentation.Dependencies.auth import UserContext, get_current_user
from src.Presentation.Dependencies.repositories import (
    get_booking_repo,
    get_service_repo,
    get_bookable_object_repo,
    get_client_booking_repo,
    get_custom_field_repo,
    get_service_rate_repo,
    get_business_customer_repo,
)
from src.Presentation.Schemas.business_schemas import CreateInternalBookingRequest

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


@router.post("/", status_code=201)
async def create_internal_booking(
    body: CreateInternalBookingRequest,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    bookable_object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    client_booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
    customer_repo: IBusinessCustomerRepository = Depends(get_business_customer_repo),
):
    use_case = CreateInternalBookingUseCase(
        service_repo=service_repo,
        bookable_object_repo=bookable_object_repo,
        client_booking_repo=client_booking_repo,
        custom_field_repo=custom_field_repo,
        rate_repo=rate_repo,
        customer_repo=customer_repo,
    )
    
    from datetime import datetime
    
    command = CreateInternalBookingCommand(
        business_id=user.business_id,
        service_id=body.service_id,
        customer_id=body.customer_id,
        actor_id=user.user_id,
        date=datetime.strptime(body.date, "%Y-%m-%d").date(),
        start_time=body.start_time,
        party_size=body.party_size,
        bookable_object_id=body.bookable_object_id,
        custom_fields=body.custom_fields,
    )
    result = await use_case.execute(command)
    return result


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
