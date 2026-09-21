from dataclasses import asdict
from fastapi import APIRouter, Depends

from src.Application.UseCases.Business.get_my_business import GetMyBusinessCommand, GetMyBusinessUseCase
from src.Application.UseCases.Business.list_my_businesses import ListMyBusinessesCommand, ListMyBusinessesUseCase
from src.Application.UseCases.Business.register_business import RegisterBusinessCommand, RegisterBusinessUseCase
from src.Application.UseCases.Business.update_business import UpdateBusinessCommand, UpdateBusinessUseCase
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Services.i_rnc_validation_service import IRncValidationService
from src.Presentation.Dependencies.auth import UserContext, get_current_user, require_admin, require_business_context
from src.Presentation.Dependencies.repositories import get_agent_metadata_repo, get_business_repo, get_business_user_repo
from src.Presentation.Dependencies.services import get_rnc_validation_service
from src.Presentation.Schemas.business_schemas import RegisterBusinessRequest, UpdateBusinessRequest

router = APIRouter()

@router.get("/me/businesses")
async def list_my_businesses(
    user: UserContext = Depends(get_current_user),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
):
    use_case = ListMyBusinessesUseCase(business_user_repo)
    command = ListMyBusinessesCommand(user_id=user.user_id)
    result = await use_case.execute(command)
    return {"items": result}

@router.post("/register", status_code=201)
async def register_business(
    body: RegisterBusinessRequest,
    user: UserContext = Depends(get_current_user),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
    business_user_repo: IBusinessUserRepository = Depends(get_business_user_repo),
    rnc_service: IRncValidationService = Depends(get_rnc_validation_service),
):
    use_case = RegisterBusinessUseCase(business_repo, agent_metadata_repo, business_user_repo, rnc_service)
    
    command = RegisterBusinessCommand(
        owner_user_id=user.user_id,
        code=body.code,
        name=body.name,
        category=body.category,
        rnc=body.rnc,
        platform=body.platform,
        address=body.address,
        phone=body.phone,
        maps_url=body.maps_url,
        aliases=body.aliases,
        schedules=[asdict(s) for s in body.schedules],
        description=body.description,
        establishment_policies=body.establishment_policies,
        pre_booking_requirements=body.pre_booking_requirements,
    )
    result = await use_case.execute(command)
    return result


@router.get("/me")
async def get_my_business(
    user: UserContext = Depends(require_business_context),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
):
    use_case = GetMyBusinessUseCase(business_repo, agent_metadata_repo)
    command = GetMyBusinessCommand(business_id=user.business_id)
    result = await use_case.execute(command)
    return result


@router.patch("/me")
async def update_my_business(
    body: UpdateBusinessRequest,
    user: UserContext = Depends(require_admin),
    business_repo: IBusinessRepository = Depends(get_business_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
):
    use_case = UpdateBusinessUseCase(business_repo, agent_metadata_repo)
    
    metadata_dict = None
    if body.agent_metadata:
        metadata_dict = {
            "description": body.agent_metadata.description,
            "establishment_policies": body.agent_metadata.establishment_policies,
            "pre_booking_requirements": body.agent_metadata.pre_booking_requirements,
        }
        
    command = UpdateBusinessCommand(
        business_id=user.business_id,
        name=body.name,
        phone=body.phone,
        address=body.address,
        maps_url=body.maps_url,
        aliases=body.aliases,
        schedules=[asdict(s) for s in body.schedules] if body.schedules is not None else None,
        agent_metadata=metadata_dict,
    )
    result = await use_case.execute(command)
    return result
