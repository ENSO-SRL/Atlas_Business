from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BusinessNotFoundError
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository


@dataclass
class GetMyBusinessCommand:
    business_id: UUID


@dataclass
class BusinessProfileResult:
    id: UUID
    code: str
    name: str
    category: str
    platform: str
    verification_status: str
    address: str
    maps_url: str | None
    phone: str
    aliases: list[str]
    schedules: list[dict]
    agent_metadata: dict
    created_at: str | None


class GetMyBusinessUseCase:
    """
    Devuelve el perfil del negocio del usuario autenticado.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        agent_metadata_repo: IAgentMetadataRepository,
    ):
        self.business_repo = business_repo
        self.agent_metadata_repo = agent_metadata_repo

    async def execute(self, command: GetMyBusinessCommand) -> BusinessProfileResult:
        business = await self.business_repo.get_by_id(command.business_id)
        if not business:
            raise BusinessNotFoundError()

        metadata = await self.agent_metadata_repo.get_by_id(business.agent_metadata_id)

        metadata_dict = {
            "description": metadata.description if metadata else "",
            "establishment_policies": metadata.establishment_policies if metadata else [],
            "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
        }

        created_at_str = business.created_at.isoformat() if business.created_at else None

        return BusinessProfileResult(
            id=business.id,
            code=business.code,
            name=business.name,
            category=business.category_name,
            platform=business.platform.value,
            verification_status=business.verification_status.value,
            address=business.address,
            maps_url=business.maps_url,
            phone=business.phone,
            aliases=business.aliases,
            schedules=business.schedules,
            agent_metadata=metadata_dict,
            created_at=created_at_str,
        )
