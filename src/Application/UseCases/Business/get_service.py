from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServiceCommand:
    service_id: UUID
    business_id: UUID


@dataclass
class PendingEditRequest:
    id: UUID
    status: str
    created_at: str | None


@dataclass
class ServiceDetailResult:
    id: UUID
    name: str
    publication_status: str
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    auto_selection_criteria: str
    billing_nature: str
    rejection_reason: str | None
    agent_metadata: dict
    pending_edit_request: PendingEditRequest | None


class GetServiceUseCase:
    """
    Obtiene el detalle completo de un servicio junto con su posible solicitud de edición activa.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_request_repo: IContentRequestRepository,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_request_repo = content_request_repo

    async def execute(self, command: GetServiceCommand) -> ServiceDetailResult:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        metadata = await self.agent_metadata_repo.get_by_id(service.agent_metadata_id)
        metadata_dict = {
            "description": metadata.description if metadata else "",
            "establishment_policies": metadata.establishment_policies if metadata else [],
            "pre_booking_requirements": metadata.pre_booking_requirements if metadata else [],
        }

        active_request = await self.content_request_repo.get_active_by_service(service.id)
        pending_request_dto = None
        if active_request:
            created_at_str = active_request.created_at.isoformat() if active_request.created_at else None
            pending_request_dto = PendingEditRequest(
                id=active_request.id,
                status=active_request.status.value,
                created_at=created_at_str,
            )

        return ServiceDetailResult(
            id=service.id,
            name=service.name,
            publication_status=service.publication_status.value,
            occupation_duration_minutes=service.occupation_duration_minutes,
            duration_nature=service.duration_nature.value,
            exposes_end_time=service.exposes_end_time,
            buffer_minutes=service.buffer_minutes,
            grid_interval_minutes=service.grid_interval_minutes,
            allows_manual_object_selection=service.allows_manual_object_selection,
            auto_selection_criteria=service.auto_selection_criteria.value,
            billing_nature=service.billing_nature.value,
            rejection_reason=service.rejection_reason,
            agent_metadata=metadata_dict,
            pending_edit_request=pending_request_dto,
        )
