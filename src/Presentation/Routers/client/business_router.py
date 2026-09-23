from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Client.get_public_business import GetPublicBusinessCommand, GetPublicBusinessUseCase
from src.Application.UseCases.Client.list_public_businesses import ListPublicBusinessesCommand, ListPublicBusinessesUseCase
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_client_business_repository import IClientBusinessRepository
from src.Presentation.Dependencies.auth import require_api_key
from src.Presentation.Dependencies.repositories import get_agent_metadata_repo, get_business_repo, get_client_business_repo
from src.Presentation.Schemas.client_schemas import PaginatedPublicBusinessDirectoryResponse

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/businesses", response_model=PaginatedPublicBusinessDirectoryResponse)
async def list_public_businesses(
    category_id: UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    client_business_repo: IClientBusinessRepository = Depends(get_client_business_repo),
):
    use_case = ListPublicBusinessesUseCase(client_business_repo)
    command = ListPublicBusinessesCommand(
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    items, total = await use_case.execute(command)
    return {"items": items, "total": total}


@router.get("/businesses/{business_id}")
async def get_public_business(
    business_id: UUID,
    business_repo: IBusinessRepository = Depends(get_business_repo),
    agent_metadata_repo: IAgentMetadataRepository = Depends(get_agent_metadata_repo),
):
    use_case = GetPublicBusinessUseCase(business_repo, agent_metadata_repo)
    command = GetPublicBusinessCommand(business_id=business_id)
    result = await use_case.execute(command)
    return result
