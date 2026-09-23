from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_client_business_repository import IClientBusinessRepository


@dataclass
class ListPublicBusinessesCommand:
    category_id: UUID | None
    page: int
    page_size: int


@dataclass
class PublicBusinessResult:
    id: UUID
    category_id: UUID
    code: str
    name: str
    address: str


class ListPublicBusinessesUseCase:
    def __init__(self, business_repo: IClientBusinessRepository):
        self.business_repo = business_repo

    async def execute(self, command: ListPublicBusinessesCommand) -> tuple[list[PublicBusinessResult], int]:
        items, total = await self.business_repo.list_published(
            category_id=command.category_id,
            page=command.page,
            page_size=command.page_size,
        )

        results = [
            PublicBusinessResult(
                id=i.id,
                category_id=i.category_id,
                code=i.code,
                name=i.name,
                address=i.address,
            )
            for i in items
        ]

        return results, total
