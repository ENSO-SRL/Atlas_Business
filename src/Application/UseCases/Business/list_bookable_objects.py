from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ServiceNotFoundError
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class ListBookableObjectsCommand:
    business_id: UUID
    service_id: UUID


@dataclass
class BookableObjectResult:
    id: UUID
    name: str | None
    min_capacity: int
    max_capacity: int
    is_active: bool


class ListBookableObjectsUseCase:
    """
    Lista los objetos reservables de un servicio.
    """

    def __init__(self, service_repo: IServiceRepository, bookable_object_repo: IBookableObjectRepository):
        self.service_repo = service_repo
        self.bookable_object_repo = bookable_object_repo

    async def execute(self, command: ListBookableObjectsCommand) -> list[BookableObjectResult]:
        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()
            
        objects = await self.bookable_object_repo.list_by_service(command.service_id)
        
        return [
            BookableObjectResult(
                id=o.id,
                name=o.name,
                min_capacity=o.min_capacity,
                max_capacity=o.max_capacity,
                is_active=o.is_active,
            )
            for o in objects
        ]
