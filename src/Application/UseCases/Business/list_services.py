from dataclasses import dataclass
from uuid import UUID

from src.Domain.Enums.publication_status import PublicationStatus
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class ListServicesCommand:
    business_id: UUID
    publication_status: str | None = None


@dataclass
class ServiceSummaryResult:
    id: UUID
    name: str
    publication_status: str
    occupation_duration_minutes: int
    duration_nature: str
    exposes_end_time: bool
    buffer_minutes: int
    grid_interval_minutes: int
    allows_manual_object_selection: bool
    billing_nature: str
    rejection_reason: str | None


class ListServicesUseCase:
    """
    Lista los servicios de un negocio, opcionalmente filtrados por status.
    """

    def __init__(self, service_repo: IServiceRepository):
        self.service_repo = service_repo

    async def execute(self, command: ListServicesCommand) -> list[ServiceSummaryResult]:
        status_enum = PublicationStatus(command.publication_status) if command.publication_status else None
        services = await self.service_repo.list_by_business(command.business_id, status_enum)

        return [
            ServiceSummaryResult(
                id=s.id,
                name=s.name,
                publication_status=s.publication_status.value,
                occupation_duration_minutes=s.occupation_duration_minutes,
                duration_nature=s.duration_nature.value,
                exposes_end_time=s.exposes_end_time,
                buffer_minutes=s.buffer_minutes,
                grid_interval_minutes=s.grid_interval_minutes,
                allows_manual_object_selection=s.allows_manual_object_selection,
                billing_nature=s.billing_nature.value,
                rejection_reason=s.rejection_reason,
            )
            for s in services
        ]
