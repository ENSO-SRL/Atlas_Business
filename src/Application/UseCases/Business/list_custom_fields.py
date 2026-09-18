from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository


@dataclass
class ListCustomFieldsCommand:
    business_id: UUID
    service_id: UUID


@dataclass
class CustomFieldResult:
    id: UUID
    label: str
    agent_note: str
    order: int
    required: bool
    visible_to_client: bool
    data_type: str
    options: list[str] | None
    minimum: float | None
    maximum: float | None


class ListCustomFieldsUseCase:
    """
    Lista los campos personalizados asociados a un servicio.
    """

    def __init__(self, custom_field_repo: ICustomFieldRepository):
        self.custom_field_repo = custom_field_repo

    async def execute(self, command: ListCustomFieldsCommand) -> list[CustomFieldResult]:
        fields = await self.custom_field_repo.list_by_service(command.service_id)

        return [
            CustomFieldResult(
                id=f.id,
                label=f.label,
                agent_note=f.agent_note,
                order=f.order,
                required=f.required,
                visible_to_client=f.visible_to_client,
                data_type=f.data_type.value,
                options=f.options,
                minimum=f.minimum,
                maximum=f.maximum,
            )
            for f in sorted(fields, key=lambda x: x.order)
        ]
