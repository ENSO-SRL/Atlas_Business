import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Application.UseCases.Business.list_bookable_objects import BookableObjectResult
from src.Domain.Entities.bookable_object import BookableObject
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository
from src.Application.Exceptions.business_exceptions import VerticalMetadataValidationError
from src.Domain.Services.bookable_object_vertical_validator_registry import BookableObjectVerticalValidatorRegistry


@dataclass
class CreateBookableObjectCommand:
    service_id: UUID
    business_id: UUID
    actor_id: UUID
    name: str | None
    min_capacity: int
    max_capacity: int
    vertical_metadata: dict[str, Any]


class CreateBookableObjectUseCase:
    """
    Crea un nuevo objeto reservable.
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

    async def execute(self, command: CreateBookableObjectCommand) -> BookableObjectResult:
        # Verificar pertenencia del servicio
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        # Validar vertical_metadata
        category = await self.service_category_repo.get_by_id(service.category_id)
        category_name = category.name if category else ""
        validator = self.vertical_registry.get_validator(category_name)
        is_valid, error_msg = validator.validate(command.vertical_metadata)
        if not is_valid:
            raise VerticalMetadataValidationError(error_msg or "Estructura de metadatos inválida.")

        try:
            object_id = uuid.uuid7()
        except AttributeError:
            object_id = uuid.uuid4()

        bookable_object = BookableObject(
            id=object_id,
            service_id=command.service_id,
            name=command.name,
            min_capacity=command.min_capacity,
            max_capacity=command.max_capacity,
            is_active=True,
            created_by=command.actor_id,
            vertical_metadata=command.vertical_metadata,
        )

        await self.bookable_object_repo.create(bookable_object)

        return BookableObjectResult(
            id=bookable_object.id,
            name=bookable_object.name,
            min_capacity=bookable_object.min_capacity,
            max_capacity=bookable_object.max_capacity,
            is_active=bookable_object.is_active,
            vertical_metadata=bookable_object.vertical_metadata or {},
        )
