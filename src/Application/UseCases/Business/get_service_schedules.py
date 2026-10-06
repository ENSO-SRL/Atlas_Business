from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class GetServiceSchedulesCommand:
    service_id: UUID
    business_id: UUID


class GetServiceSchedulesUseCase:
    """
    Obtiene únicamente los horarios de un servicio,
    validando que pertenezca al negocio del usuario.
    """

    def __init__(self, service_repo: IServiceRepository):
        self.service_repo = service_repo

    async def execute(self, command: GetServiceSchedulesCommand) -> list[dict[str, Any]]:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        return [
            {
                "weekday": s.weekday.value,
                "opening_time": s.opening_time.isoformat(),
                "closing_time": s.closing_time.isoformat(),
            }
            for s in service.schedules
        ]
