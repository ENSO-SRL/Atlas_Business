from datetime import date
from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Client.get_available_objects import GetAvailableObjectsCommand, GetAvailableObjectsUseCase
from src.Application.UseCases.Client.get_public_service import GetPublicServiceCommand, GetPublicServiceUseCase
from src.Application.UseCases.Client.get_service_availability import GetServiceAvailabilityCommand, GetServiceAvailabilityUseCase
from src.Application.UseCases.Client.get_service_rates_public import GetServiceRatesPublicCommand, GetServiceRatesPublicUseCase
from src.Application.UseCases.Client.list_public_services import ListPublicServicesCommand, ListPublicServicesUseCase
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Presentation.Dependencies.auth import require_api_key
from src.Presentation.Dependencies.repositories import (
    get_agent_metadata_repo,
    get_bookable_object_repo,
    get_business_repo,
    get_client_booking_repo,
    get_client_service_repo,
    get_custom_field_repo,
    get_service_rate_repo,
)

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/businesses/{business_id}/services")
async def list_public_services(
    business_id: UUID,
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = ListPublicServicesUseCase(business_repo, service_repo,agent_metadata_repo, custom_field_repo)
    command = ListPublicServicesCommand(business_id=business_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.get("/businesses/{business_id}/services/{service_id}")
async def get_public_service(
    business_id: UUID,
    service_id: UUID,
    business_repo: IBusinessRepository = Depends(get_business_repo),
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = GetPublicServiceUseCase(business_repo, service_repo, agent_metadata_repo, custom_field_repo)
    command = GetPublicServiceCommand(business_id=business_id, service_id=service_id)
    result = await use_case.execute(command)
    return result


@router.get("/services/{service_id}/rates")
async def get_service_rates_public(
    service_id: UUID,
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = GetServiceRatesPublicUseCase(service_repo, rate_repo)
    command = GetServiceRatesPublicCommand(service_id=service_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.get("/services/{service_id}/availability")
async def get_service_availability(
    service_id: UUID,
    filter_date: date,
    party_size: int | None = None,
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = GetServiceAvailabilityUseCase(service_repo, business_repo, object_repo, booking_repo, rate_repo)
    command = GetServiceAvailabilityCommand(
        service_id=service_id,
        party_size=party_size,
        date=filter_date,
    )
    result = await use_case.execute(command)
    return {"slots": result}


@router.get("/services/{service_id}/bookable-objects")
async def get_available_objects(
    service_id: UUID,
    target_date: date,
    start_time: str,
    party_size: int | None = None,
    service_repo: IClientServiceRepository = Depends(get_client_service_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
):
    use_case = GetAvailableObjectsUseCase(service_repo, object_repo, booking_repo)
    command = GetAvailableObjectsCommand(
        service_id=service_id,
        date=target_date,
        party_size=party_size,
        start_time=start_time,
    )
    result = await use_case.execute(command)
    return {"items": result}
