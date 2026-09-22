import uuid
from dataclasses import dataclass

from src.Domain.Entities.business_category import BusinessCategory
from src.Domain.Ports.Repositories.i_business_category_repository import IBusinessCategoryRepository


@dataclass
class CreateBusinessCategoryCommand:
    name: str
    description: str | None = None


class CreateBusinessCategoryUseCase:
    def __init__(self, repo: IBusinessCategoryRepository):
        self._repo = repo

    async def execute(self, command: CreateBusinessCategoryCommand) -> BusinessCategory:
        try:
            entity_id = uuid.uuid7()
        except AttributeError:
            entity_id = uuid.uuid4()

        category = BusinessCategory(
            id=entity_id,
            name=command.name,
            description=command.description,
        )
        return await self._repo.create(category)


@dataclass
class ListBusinessCategoriesQuery:
    only_active: bool = True


class ListBusinessCategoriesUseCase:
    def __init__(self, repo: IBusinessCategoryRepository):
        self._repo = repo

    async def execute(self, query: ListBusinessCategoriesQuery) -> list[BusinessCategory]:
        return await self._repo.list_all(only_active=query.only_active)


@dataclass
class UpdateBusinessCategoryCommand:
    category_id: uuid.UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class UpdateBusinessCategoryUseCase:
    def __init__(self, repo: IBusinessCategoryRepository):
        self._repo = repo

    async def execute(self, command: UpdateBusinessCategoryCommand) -> BusinessCategory:
        from src.Application.Exceptions.business_exceptions import BusinessCategoryNotFoundError
        category = await self._repo.get_by_id(command.category_id)
        if not category:
            raise BusinessCategoryNotFoundError()

        if command.name is not None:
            category.name = command.name
        if command.description is not None:
            category.description = command.description
        if command.is_active is not None:
            category.is_active = command.is_active

        return await self._repo.update(category)


@dataclass
class DeleteBusinessCategoryCommand:
    category_id: uuid.UUID


class DeleteBusinessCategoryUseCase:
    def __init__(self, repo: IBusinessCategoryRepository):
        self._repo = repo

    async def execute(self, command: DeleteBusinessCategoryCommand) -> None:
        from src.Application.Exceptions.business_exceptions import BusinessCategoryNotFoundError
        category = await self._repo.get_by_id(command.category_id)
        if not category:
            raise BusinessCategoryNotFoundError()

        # Soft delete
        category.is_deleted = True
        category.is_active = False
        await self._repo.update(category)
