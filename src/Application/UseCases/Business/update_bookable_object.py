from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BookableObjectNotFoundError, ServiceNotFoundError
from src.Application.UseCases.Business.list_bookable_objects import BookableObjectResult
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Application.Exceptions.business_exceptions import VerticalMetadataValidationError
from src.Domain.Services.bookable_object_vertical_validator_registry import BookableObjectVerticalValidatorRegistry


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
    vertical_metadata: dict[str, Any] | None = None


class UpdateBookableObjectUseCase:
    """
    Actualiza un objeto reservable.
    """

    def __init__(
        self,
        bookable_object_repo: IBookableObjectRepository,
        service_repo: IServiceRepository,
        service_category_repo: IServiceCategoryRepository,
    ):
        self.bookable_object_repo = bookable_object_repo
        self.service_repo = service_repo
        self.service_category_repo = service_category_repo
        self.vertical_registry = BookableObjectVerticalValidatorRegistry()

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
            
        if command.vertical_metadata is not None:
            category = await self.service_category_repo.get_by_id(service.category_id)
            category_name = category.name if category else ""
            validator = self.vertical_registry.get_validator(category_name)
            is_valid, error_msg = validator.validate(command.vertical_metadata)
            if not is_valid:
                raise VerticalMetadataValidationError(error_msg or "Estructura de metadatos inválida.")
            bookable_object.vertical_metadata = command.vertical_metadata
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
            vertical_metadata=bookable_object.vertical_metadata or {},
        )
