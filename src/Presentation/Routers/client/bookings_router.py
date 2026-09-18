from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Client.create_booking import CreateBookingCommand, CreateBookingUseCase
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Presentation.Dependencies.auth import require_api_key
from src.Presentation.Dependencies.repositories import (
    get_bookable_object_repo,
    get_client_booking_repo,
    get_client_service_repo,
    get_custom_field_repo,
    get_service_rate_repo,
)
from src.Presentation.Schemas.client_schemas import CreateBookingRequest

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/services/{service_id}/bookings", status_code=201)
async def create_booking(
    service_id: UUID,
    body: CreateBookingRequest,
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = CreateBookingUseCase(
        service_repo,
        rate_repo,
        object_repo,
        booking_repo,
        custom_field_repo,
    )
    command = CreateBookingCommand(
        service_id=service_id,
        date=body.date,
        start_time=body.start_time,
        party_size=body.party_size,
        bookable_object_id=body.bookable_object_id,
        custom_fields=body.custom_fields,
    )
    result = await use_case.execute(command)
    return result
