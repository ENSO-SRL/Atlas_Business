from src.Presentation.Dependencies.repositories import get_business_repo
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from fastapi import APIRouter, Depends
from uuid import UUID

# Use Cases
from src.Application.UseCases.Business.create_service import CreateServiceCommand, CreateServiceUseCase
from src.Application.UseCases.Business.list_services import ListServicesCommand, ListServicesUseCase
from src.Application.UseCases.Business.get_service import GetServiceCommand, GetServiceUseCase
from src.Application.UseCases.Business.update_service import UpdateServiceCommand, UpdateServiceUseCase

from src.Application.UseCases.Business.create_bookable_object import CreateBookableObjectCommand, CreateBookableObjectUseCase
from src.Application.UseCases.Business.list_bookable_objects import ListBookableObjectsCommand, ListBookableObjectsUseCase
from src.Application.UseCases.Business.update_bookable_object import UpdateBookableObjectCommand, UpdateBookableObjectUseCase

from src.Application.UseCases.Business.get_service_rates import GetServiceRatesCommand, GetServiceRatesUseCase
from src.Application.UseCases.Business.replace_service_rates import ReplaceServiceRatesCommand, ReplaceServiceRatesUseCase, RateInput

from src.Application.UseCases.Business.create_custom_field import CreateCustomFieldCommand, CreateCustomFieldUseCase
from src.Application.UseCases.Business.delete_custom_field import DeleteCustomFieldCommand, DeleteCustomFieldUseCase
from src.Application.UseCases.Business.list_custom_fields import ListCustomFieldsCommand, ListCustomFieldsUseCase

from src.Application.UseCases.Business.get_service_availability import GetServiceAvailabilityCommand, GetServiceAvailabilityUseCase
from src.Application.UseCases.Business.get_available_objects import GetAvailableObjectsCommand, GetAvailableObjectsUseCase

# Ports
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService

# Dependencies
from src.Presentation.Dependencies.auth import UserContext, get_current_user, require_admin
from src.Presentation.Dependencies.repositories import (
    get_agent_metadata_repo,
    get_bookable_object_repo,
    get_content_request_repo,
    get_custom_field_repo,
    get_service_category_repo,
    get_service_rate_repo,
    get_service_repo,
    get_client_booking_repo,
)
from src.Presentation.Dependencies.services import get_content_filter_service
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Presentation.Schemas.business_schemas import (
    CreateBookableObjectRequest,
    CreateCustomFieldRequest,
    CreateServiceRequest,
    ReplaceRatesRequest,
    UpdateBookableObjectRequest,
    UpdateServiceRequest,
)

router = APIRouter()


# ─── Servicios ───

@router.get("/")
async def list_services(
    status: str | None = None,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
):
    use_case = ListServicesUseCase(service_repo)
    command = ListServicesCommand(business_id=user.business_id, publication_status=status)
    result = await use_case.execute(command)
    return {"items": result}


@router.post("/", status_code=201)
async def create_service(
    body: CreateServiceRequest,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    content_filter: IContentFilterService = Depends(get_content_filter_service),
    service_category_repo: IServiceCategoryRepository = Depends(get_service_category_repo),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = CreateServiceUseCase(
        service_repo, agent_metadata_repo, content_filter, service_category_repo, business_repo, rate_repo
    )
    
    mapped_rates = None
    if body.rates:
        mapped_rates = [
            RateInput(
                weekdays=r.weekdays,
                start_time=r.start_time,
                end_time=r.end_time,
                amount=r.amount,
                calculation_basis=r.calculation_basis,
            ) for r in body.rates
        ]
    
    command = CreateServiceCommand(
        business_id=user.business_id,
        name=body.name,
        category_id=body.category_id,
        occupation_duration_minutes=body.occupation_duration_minutes,
        duration_nature=body.duration_nature,
        exposes_end_time=body.exposes_end_time,
        buffer_minutes=body.buffer_minutes,
        grid_interval_minutes=body.grid_interval_minutes,
        allows_manual_object_selection=body.allows_manual_object_selection,
        auto_selection_criteria=body.auto_selection_criteria,
        billing_nature=body.billing_nature,
        description=body.agent_metadata.description,
        establishment_policies=body.agent_metadata.establishment_policies,
        pre_booking_requirements=body.agent_metadata.pre_booking_requirements,
        rates=mapped_rates,
        actor_id=user.user_id,
    )
    result = await use_case.execute(command)
    return result


@router.get("/{service_id}")
async def get_service(
    service_id: UUID,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    content_req_repo: IContentRequestRepository = Depends(get_content_request_repo),
):
    use_case = GetServiceUseCase(service_repo, agent_metadata_repo, content_req_repo)
    command = GetServiceCommand(business_id=user.business_id, service_id=service_id)
    result = await use_case.execute(command)
    return result


@router.patch("/{service_id}")
async def update_service(
    service_id: UUID,
    body: UpdateServiceRequest,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    content_req_repo: IContentRequestRepository = Depends(get_content_request_repo),
    content_filter: IContentFilterService = Depends(get_content_filter_service),
    service_category_repo: IServiceCategoryRepository = Depends(get_service_category_repo),
):
    use_case = UpdateServiceUseCase(service_repo, agent_metadata_repo, content_req_repo, content_filter, service_category_repo)
    
    metadata_dict = None
    if body.agent_metadata:
        metadata_dict = {
            "description": body.agent_metadata.description,
            "establishment_policies": body.agent_metadata.establishment_policies,
            "pre_booking_requirements": body.agent_metadata.pre_booking_requirements,
        }
        
    command = UpdateServiceCommand(
        business_id=user.business_id,
        service_id=service_id,
        name=body.name,
        category_id=body.category_id,
        buffer_minutes=body.buffer_minutes,
        grid_interval_minutes=body.grid_interval_minutes,
        exposes_end_time=body.exposes_end_time,
        description=body.agent_metadata.description,
        establishment_policies=body.agent_metadata.establishment_policies,
        pre_booking_requirements=body.agent_metadata.pre_booking_requirements,
        #agent_metadata=metadata_dict,
        actor_id=user.user_id,
    )
    result = await use_case.execute(command)
    return result


# ─── Objetos Reservables ───

@router.get("/{service_id}/bookable-objects")
async def list_bookable_objects(
    service_id: UUID,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
):
    use_case = ListBookableObjectsUseCase(service_repo, object_repo)
    command = ListBookableObjectsCommand(business_id=user.business_id, service_id=service_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.post("/{service_id}/bookable-objects", status_code=201)
async def create_bookable_object(
    service_id: UUID,
    body: CreateBookableObjectRequest,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
):
    use_case = CreateBookableObjectUseCase(object_repo, service_repo)
    command = CreateBookableObjectCommand(
        business_id=user.business_id,
        service_id=service_id,
        name=body.name,
        min_capacity=body.min_capacity,
        max_capacity=body.max_capacity,
        actor_id=user.user_id,
    )
    result = await use_case.execute(command)
    return result


@router.patch("/{service_id}/bookable-objects/{object_id}")
async def update_bookable_object(
    service_id: UUID,
    object_id: UUID,
    body: UpdateBookableObjectRequest,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
):
    use_case = UpdateBookableObjectUseCase(object_repo, service_repo)
    command = UpdateBookableObjectCommand(
        business_id=user.business_id,
        service_id=service_id,
        object_id=object_id,
        name=body.name,
        min_capacity=body.min_capacity,
        max_capacity=body.max_capacity,
        is_active=body.is_active,
        actor_id=user.user_id,
    )
    result = await use_case.execute(command)
    return result


# ─── Tarifas ───

@router.get("/{service_id}/rates")
async def get_service_rates(
    service_id: UUID,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = GetServiceRatesUseCase(service_repo, rate_repo)
    command = GetServiceRatesCommand(business_id=user.business_id, service_id=service_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.put("/{service_id}/rates")
async def replace_service_rates(
    service_id: UUID,
    body: ReplaceRatesRequest,
    user: UserContext = Depends(require_admin),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    service_repo: IServiceRepository = Depends(get_service_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = ReplaceServiceRatesUseCase(rate_repo, service_repo, business_repo)
    
    rates_data = [
        {
            "weekdays": r.weekdays,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "amount": r.amount,
            "calculation_basis": r.calculation_basis,
        }
        for r in body.rates
    ]
    
    command = ReplaceServiceRatesCommand(
        business_id=user.business_id,
        service_id=service_id,
        rates=rates_data,
        actor_id=user.user_id
    )
    result = await use_case.execute(command)
    return {"items": result}


# ─── Campos Personalizados ───

@router.get("/{service_id}/custom-fields")
async def list_custom_fields(
    service_id: UUID,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = ListCustomFieldsUseCase(service_repo, custom_field_repo)
    command = ListCustomFieldsCommand(business_id=user.business_id, service_id=service_id)
    result = await use_case.execute(command)
    return {"items": result}


@router.post("/{service_id}/custom-fields", status_code=201)
async def create_custom_field(
    service_id: UUID,
    body: CreateCustomFieldRequest,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = CreateCustomFieldUseCase(custom_field_repo, service_repo)
    command = CreateCustomFieldCommand(
        business_id=user.business_id,
        service_id=service_id,
        label=body.label,
        agent_note=body.agent_note,
        order=body.order,
        required=body.required,
        visible_to_client=body.visible_to_client,
        data_type=body.data_type,
        options=body.options,
        minimum=body.minimum,
        maximum=body.maximum,
        actor_id=user.user_id,
    )
    result = await use_case.execute(command)
    return result


@router.delete("/{service_id}/custom-fields/{field_id}", status_code=204)
async def delete_custom_field(
    service_id: UUID,
    field_id: UUID,
    user: UserContext = Depends(require_admin),
    service_repo: IServiceRepository = Depends(get_service_repo),
    custom_field_repo: ICustomFieldRepository = Depends(get_custom_field_repo),
):
    use_case = DeleteCustomFieldUseCase(service_repo, custom_field_repo)
    command = DeleteCustomFieldCommand(
        business_id=user.business_id,
        service_id=service_id,
        field_id=field_id,
    )
    await use_case.execute(command)
    return None


# ─── Disponibilidad ───

from datetime import date

@router.get("/{service_id}/availability")
async def get_service_availability(
    service_id: UUID,
    date_val: date,
    party_size: int = 1,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    bookable_object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    client_booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
    rate_repo: IServiceRateRepository = Depends(get_service_rate_repo),
):
    use_case = GetServiceAvailabilityUseCase(
        service_repo=service_repo,
        business_repo=business_repo,
        bookable_object_repo=bookable_object_repo,
        client_booking_repo=client_booking_repo,
        rate_repo=rate_repo,
    )
    command = GetServiceAvailabilityCommand(
        business_id=user.business_id,
        service_id=service_id,
        date=date_val,
        party_size=party_size,
    )
    return await use_case.execute(command)


@router.get("/{service_id}/availability/objects")
async def get_available_objects(
    service_id: UUID,
    date_val: date,
    start_time: str,
    party_size: int = 1,
    user: UserContext = Depends(get_current_user),
    service_repo: IServiceRepository = Depends(get_service_repo),
    bookable_object_repo: IBookableObjectRepository = Depends(get_bookable_object_repo),
    client_booking_repo: IClientBookingRepository = Depends(get_client_booking_repo),
):
    use_case = GetAvailableObjectsUseCase(
        service_repo=service_repo,
        bookable_object_repo=bookable_object_repo,
        client_booking_repo=client_booking_repo,
    )
    command = GetAvailableObjectsCommand(
        business_id=user.business_id,
        service_id=service_id,
        date=date_val,
        start_time=start_time,
        party_size=party_size,
    )
    return await use_case.execute(command)
