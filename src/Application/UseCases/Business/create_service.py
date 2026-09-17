import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Domain.Entities.agent_metadata import AgentMetadata
from src.Domain.Entities.service import Service
from src.Domain.Enums.auto_selection import AutoSelectionCriteria
from src.Domain.Enums.billing_nature import BillingNature
from src.Domain.Enums.duration_nature import DurationNature
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService


@dataclass
class CreateServiceCommand:
    business_id: UUID
    actor_id: UUID
    name: str
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    auto_selection_criteria: str
    billing_nature: str
    description: str
    establishment_policies: list[str]
    pre_booking_requirements: list[str]


@dataclass
class CreateServiceResult:
    id: UUID
    name: str
    publication_status: str
    message: str


class CreateServiceUseCase:
    """
    Crea un nuevo servicio pasando por el filtro de contenido.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_filter: IContentFilterService,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_filter = content_filter

    async def execute(self, command: CreateServiceCommand) -> CreateServiceResult:
        try:
            metadata_id = uuid.uuid7()
        except AttributeError:
            metadata_id = uuid.uuid4()

        metadata = AgentMetadata(
            id=metadata_id,
            description=command.description,
            establishment_policies=command.establishment_policies,
            pre_booking_requirements=command.pre_booking_requirements,
            created_by=command.actor_id,
        )
        await self.agent_metadata_repo.create(metadata)

        try:
            service_id = uuid.uuid7()
        except AttributeError:
            service_id = uuid.uuid4()

        # Solo enviamos campos de texto libre al filtro
        matches = await self.content_filter.check(
            {
                "name": command.name,
                "description": command.description,
            }
        )

        initial_status = PublicationStatus.UNDER_REVIEW if matches else PublicationStatus.PUBLISHED
        message = "En revisión por posible contenido restringido." if matches else "Servicio publicado exitosamente."

        service = Service(
            id=service_id,
            business_id=command.business_id,
            name=command.name,
            occupation_duration_minutes=command.occupation_duration_minutes,
            duration_nature=DurationNature(command.duration_nature),
            exposes_end_time=command.exposes_end_time,
            buffer_minutes=command.buffer_minutes,
            grid_interval_minutes=command.grid_interval_minutes,
            allows_manual_object_selection=command.allows_manual_object_selection,
            auto_selection_criteria=AutoSelectionCriteria(command.auto_selection_criteria),
            billing_nature=BillingNature(command.billing_nature),
            agent_metadata_id=metadata_id,
            publication_status=initial_status,
            created_by=command.actor_id,
        )
        
        await self.service_repo.create(service)

        return CreateServiceResult(
            id=service.id,
            name=service.name,
            publication_status=service.publication_status.value,
            message=message,
        )
