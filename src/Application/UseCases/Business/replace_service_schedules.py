from dataclasses import dataclass
from datetime import time
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Entities.service import ServiceSchedule
from src.Domain.Enums.weekday import Weekday
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class ReplaceServiceSchedulesCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    schedules: list[dict[str, Any]]


class ReplaceServiceSchedulesUseCase:
    """
    Reemplaza íntegramente los horarios operativos de un servicio.
    Al ser atributos operativos, no pasan por moderación de IA.
    """

    def __init__(self, service_repo: IServiceRepository):
        self.service_repo = service_repo

    async def execute(self, command: ReplaceServiceSchedulesCommand) -> None:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        new_schedules = []
        for s in command.schedules:
            new_schedules.append(
                ServiceSchedule(
                    weekday=Weekday(s["weekday"]),
                    opening_time=time.fromisoformat(s["opening_time"]),
                    closing_time=time.fromisoformat(s["closing_time"]),
                )
            )

        # La validación de dominio saltará automáticamente si hay duplicados o > 7
        # Pero los dataclasses validan en __post_init__, y como aquí estamos reemplazando un atributo,
        # la validación a nivel entidad no se ejecutará a menos que la forcemos o validemos explícitamente.
        # Por seguridad de diseño, reasignamos e invocamos __post_init__ simulado o hacemos la validación manual.
        
        dias = [s.weekday for s in new_schedules]
        if len(new_schedules) > 7:
            raise ValueError("schedules no puede tener más de 7 entradas.")
        if len(dias) != len(set(dias)):
            raise ValueError("schedules no puede contener días duplicados para el servicio.")

        service.schedules = new_schedules
        service.updated_by = command.actor_id

        await self.service_repo.update(service)
