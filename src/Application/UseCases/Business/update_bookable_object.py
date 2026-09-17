from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BookableObjectNotFoundError, ServiceNotFoundError
from src.Application.UseCases.Business.list_bookable_objects import BookableObjectResult
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class UpdateBookableObjectCommand:
    object_id: UUID
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    name: str | None = None
    min_capacity: int | None = None
    max_capacity: int | None = None
    is_active: bool | None = None


class UpdateBookableObjectUseCase:
    """
    Actualiza un objeto reservable.
    """

    def __init__(
        self,
        bookable_object_repo: IBookableObjectRepository,
        service_repo: IServiceRepository,
    ):
        self.bookable_object_repo = bookable_object_repo
        self.service_repo = service_repo

    async def execute(self, command: UpdateBookableObjectCommand) -> BookableObjectResult:
        # Verificar pertenencia del servicio
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        bookable_object = await self.bookable_object_repo.get_by_id(command.object_id, command.service_id)
        if not bookable_object:
            raise BookableObjectNotFoundError()

        changed = False
        if command.name is not None:
            bookable_object.name = command.name
            changed = True
        if command.min_capacity is not None:
            bookable_object.min_capacity = command.min_capacity
            changed = True
        if command.max_capacity is not None:
            bookable_object.max_capacity = command.max_capacity
            changed = True
        if command.is_active is not None:
            bookable_object.is_active = command.is_active
            changed = True

        if changed:
            bookable_object.updated_at = datetime.now(timezone.utc)
            bookable_object.updated_by = command.actor_id
            await self.bookable_object_repo.update(bookable_object)

        return BookableObjectResult(
            id=bookable_object.id,
            name=bookable_object.name,
            min_capacity=bookable_object.min_capacity,
            max_capacity=bookable_object.max_capacity,
            is_active=bookable_object.is_active,
        )
