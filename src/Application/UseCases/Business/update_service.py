import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError, ServiceNotPublishedError
from src.Domain.Entities.content_request import ContentRequest
from src.Domain.Enums.content_request_status import ContentRequestStatus
from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_content_request_repository import IContentRequestRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService


@dataclass
class UpdateServiceCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    name: str | None = None
    description: str | None = None
    establishment_policies: list[str] | None = None
    pre_booking_requirements: list[str] | None = None
    # Campos operativos (precio/capacidad): NO pasan por el filtro
    buffer_minutes: int | None = None
    grid_interval_minutes: int | None = None
    exposes_end_time: bool | None = None


@dataclass
class UpdateServiceResult:
    content_request_id: UUID | None
    status: str
    message: str


class UpdateServiceUseCase:
    """
    Edita un servicio. Implementa el patrón shadow edit.
    Si hay cambios de texto, pasan por el filtro de contenido.
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        content_request_repo: IContentRequestRepository,
        content_filter: IContentFilterService,
    ):
        self.service_repo = service_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.content_request_repo = content_request_repo
        self.content_filter = content_filter

    async def execute(self, command: UpdateServiceCommand) -> UpdateServiceResult:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        if service.publication_status != PublicationStatus.PUBLISHED:
            raise ServiceNotPublishedError()

        # Construir payload de cambios
        payload = {}
        if command.name is not None and command.name != service.name:
            payload["name"] = command.name
        if command.buffer_minutes is not None and command.buffer_minutes != service.buffer_minutes:
            payload["buffer_minutes"] = command.buffer_minutes
        if command.grid_interval_minutes is not None and command.grid_interval_minutes != service.grid_interval_minutes:
            payload["grid_interval_minutes"] = command.grid_interval_minutes
        if command.exposes_end_time is not None and command.exposes_end_time != service.exposes_end_time:
            payload["exposes_end_time"] = command.exposes_end_time

        metadata = await self.agent_metadata_repo.get_by_id(service.agent_metadata_id)
        
        if command.description is not None and (not metadata or command.description != metadata.description):
            payload["description"] = command.description
        if command.establishment_policies is not None and (not metadata or command.establishment_policies != metadata.establishment_policies):
            payload["establishment_policies"] = command.establishment_policies
        if command.pre_booking_requirements is not None and (not metadata or command.pre_booking_requirements != metadata.pre_booking_requirements):
            payload["pre_booking_requirements"] = command.pre_booking_requirements

        if not payload:
            return UpdateServiceResult(content_request_id=None, status="NO_CHANGES", message="No hay cambios para aplicar.")

        # Buscar solicitud activa previa
        active_request = await self.content_request_repo.get_active_by_service(service.id)
        if active_request:
            active_request.status = ContentRequestStatus.SUPERSEDED
            active_request.updated_at = datetime.now(timezone.utc)
            active_request.updated_by = command.actor_id
            await self.content_request_repo.update(active_request)

        # Correr filtro de contenido sobre campos de texto libre
        text_fields_to_check = {
            k: v for k, v in payload.items() 
            if k in ("name", "description")
        }
        
        matches = []
        if text_fields_to_check:
            matches = await self.content_filter.check(text_fields_to_check)

        try:
            request_id = uuid.uuid7()
        except AttributeError:
            request_id = uuid.uuid4()

        if not matches:
            # Aplicar cambios directamente
            if "name" in payload: service.name = payload["name"]
            if "buffer_minutes" in payload: service.buffer_minutes = payload["buffer_minutes"]
            if "grid_interval_minutes" in payload: service.grid_interval_minutes = payload["grid_interval_minutes"]
            if "exposes_end_time" in payload: service.exposes_end_time = payload["exposes_end_time"]
            
            if metadata:
                if "description" in payload: metadata.description = payload["description"]
                if "establishment_policies" in payload: metadata.establishment_policies = payload["establishment_policies"]
                if "pre_booking_requirements" in payload: metadata.pre_booking_requirements = payload["pre_booking_requirements"]

            now = datetime.now(timezone.utc)
            service.updated_at = now
            service.updated_by = command.actor_id
            await self.service_repo.update(service)
            
            if metadata:
                metadata.updated_at = now
                metadata.updated_by = command.actor_id
                await self.agent_metadata_repo.update(metadata)

            # Trazabilidad
            content_req = ContentRequest(
                id=request_id,
                service_id=service.id,
                status=ContentRequestStatus.APPROVED,
                payload=payload,
                filter_matches=[],
                created_by=command.actor_id
            )
            await self.content_request_repo.create(content_req)
            
            return UpdateServiceResult(
                content_request_id=request_id,
                status=ContentRequestStatus.APPROVED.value,
                message="Edición aplicada de inmediato."
            )
        else:
            # Crear ContentRequest para revisión (Shadow Edit)
            content_req = ContentRequest(
                id=request_id,
                service_id=service.id,
                status=ContentRequestStatus.UNDER_REVIEW,
                payload=payload,
                filter_matches=matches,
                created_by=command.actor_id
            )
            await self.content_request_repo.create(content_req)

            return UpdateServiceResult(
                content_request_id=request_id,
                status=ContentRequestStatus.UNDER_REVIEW.value,
                message="La edición está en revisión por posible contenido restringido."
            )
