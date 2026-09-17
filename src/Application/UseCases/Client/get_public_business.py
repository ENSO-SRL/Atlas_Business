from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.client_exceptions import BusinessNotVerifiedError
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository


@dataclass
class GetPublicBusinessCommand:
    business_id: UUID


@dataclass
class PublicBusinessResult:
    id: UUID
    name: str
    category: str
    platform: str
    address: str
    maps_url: str | None
    phone: str
    schedules: list[dict]
    agent_metadata: dict


class GetPublicBusinessUseCase:
    """
    Devuelve información pública de un negocio, solo si está verificado.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        agent_metadata_repo: IAgentMetadataRepository,
    ):
        self.business_repo = business_repo
        self.agent_metadata_repo = agent_metadata_repo

    async def execute(self, command: GetPublicBusinessCommand) -> PublicBusinessResult:
        business = await self.business_repo.get_by_id(command.business_id)
        
        if not business or business.verification_status != VerificationStatus.VERIFIED:
            raise BusinessNotVerifiedError()

        metadata = await self.agent_metadata_repo.get_by_id(business.agent_metadata_id)
        
        metadata_dict = {
            "description": metadata.description if metadata else "",
            "establishment_policies": metadata.establishment_policies if metadata else [],
            "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
        }

        return PublicBusinessResult(
            id=business.id,
            name=business.name,
            category=business.category,
            platform=business.platform.value,
            address=business.address,
            maps_url=business.maps_url,
            phone=business.phone,
            schedules=business.schedules,
            agent_metadata=metadata_dict,
        )
