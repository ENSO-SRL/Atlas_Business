import uuid
from dataclasses import dataclass

from src.Domain.Entities.service_category import ServiceCategory
from src.Domain.Ports.Repositories.i_service_category_repository import IServiceCategoryRepository


@dataclass
class CreateServiceCategoryCommand:
    name: str
    description: str | None = None


class CreateServiceCategoryUseCase:
    def __init__(self, repo: IServiceCategoryRepository):
        self._repo = repo

    async def execute(self, command: CreateServiceCategoryCommand) -> ServiceCategory:
        try:
            entity_id = uuid.uuid7()
        except AttributeError:
            entity_id = uuid.uuid4()

        category = ServiceCategory(
            id=entity_id,
            name=command.name,
            description=command.description,
        )
        return await self._repo.create(category)


@dataclass
class ListServiceCategoriesQuery:
    only_active: bool = True


class ListServiceCategoriesUseCase:
    def __init__(self, repo: IServiceCategoryRepository):
        self._repo = repo

    async def execute(self, query: ListServiceCategoriesQuery) -> list[ServiceCategory]:
        return await self._repo.list_all(only_active=query.only_active)


@dataclass
class UpdateServiceCategoryCommand:
    category_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class UpdateServiceCategoryUseCase:
    def __init__(self, repo: IServiceCategoryRepository):
        self._repo = repo

    async def execute(self, command: UpdateServiceCategoryCommand) -> ServiceCategory:
        from src.Application.Exceptions.business_exceptions import ServiceCategoryNotFoundError
        category = await self._repo.get_by_id(command.category_id)
        if not category:
            raise ServiceCategoryNotFoundError()

        if command.name is not None:
            category.name = command.name
        if command.description is not None:
            category.description = command.description
        if command.is_active is not None:
            category.is_active = command.is_active

        return await self._repo.update(category)


@dataclass
class DeleteServiceCategoryCommand:
    category_id: uuid.UUID


class DeleteServiceCategoryUseCase:
    def __init__(self, repo: IServiceCategoryRepository):
        self._repo = repo

    async def execute(self, command: DeleteServiceCategoryCommand) -> None:
        from src.Application.Exceptions.business_exceptions import ServiceCategoryNotFoundError
        category = await self._repo.get_by_id(command.category_id)
        if not category:
            raise ServiceCategoryNotFoundError()

        # Soft delete
        category.is_deleted = True
        category.is_active = False
        await self._repo.update(category)
