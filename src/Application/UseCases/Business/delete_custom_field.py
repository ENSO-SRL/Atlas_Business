from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import CustomFieldNotFoundError, ServiceNotFoundError
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class DeleteCustomFieldCommand:
    field_id: UUID
    service_id: UUID
    business_id: UUID


class DeleteCustomFieldUseCase:
    """
    Elimina un campo personalizado, validando pertenencia.
    """

    def __init__(self, service_repo: IServiceRepository, custom_field_repo: ICustomFieldRepository):
        self.service_repo = service_repo
        self.custom_field_repo = custom_field_repo

    async def execute(self, command: DeleteCustomFieldCommand) -> None:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()
        field = await self.custom_field_repo.get_by_id(command.field_id, command.service_id)
        if not field:
            raise CustomFieldNotFoundError()

        await self.custom_field_repo.delete(command.field_id)
