from fastapi import APIRouter, Depends
from uuid import UUID

from src.Application.UseCases.Client.get_public_business import GetPublicBusinessCommand, GetPublicBusinessUseCase
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Presentation.Dependencies.auth import require_api_key
from src.Presentation.Dependencies.repositories import get_agent_metadata_repo, get_business_repo

router = APIRouter(dependencies=[Depends(require_api_key)])


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
