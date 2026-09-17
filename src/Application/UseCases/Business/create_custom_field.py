import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Application.UseCases.Business.list_custom_fields import CustomFieldResult
from src.Domain.Entities.custom_field import CustomField
from src.Domain.Enums.data_type import DataType
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class CreateCustomFieldCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    label: str
    agent_note: str
    order: int
    required: bool
    visible_to_client: bool
    data_type: str
    options: list[str] | None = None
    minimum: float | None = None
    maximum: float | None = None


class CreateCustomFieldUseCase:
    """
    Crea un nuevo campo personalizado para un servicio.
    La validación de consistencia (opciones vs data_type) la hace la entidad CustomField.
    """

    def __init__(
        self,
        custom_field_repo: ICustomFieldRepository,
        service_repo: IServiceRepository,
    ):
        self.custom_field_repo = custom_field_repo
        self.service_repo = service_repo

    async def execute(self, command: CreateCustomFieldCommand) -> CustomFieldResult:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        try:
            field_id = uuid.uuid7()
        except AttributeError:
            field_id = uuid.uuid4()

        field = CustomField(
            id=field_id,
            business_id=command.business_id,
            service_id=command.service_id,
            label=command.label,
            agent_note=command.agent_note,
            order=command.order,
            required=command.required,
            visible_to_client=command.visible_to_client,
            data_type=DataType(command.data_type),
            options=command.options,
            minimum=command.minimum,
            maximum=command.maximum,
            created_by=command.actor_id,
        )

        await self.custom_field_repo.create(field)

        return CustomFieldResult(
            id=field.id,
            label=field.label,
            agent_note=field.agent_note,
            order=field.order,
            required=field.required,
            visible_to_client=field.visible_to_client,
            data_type=field.data_type.value,
            options=field.options,
            minimum=field.minimum,
            maximum=field.maximum,
        )
