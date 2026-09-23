from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository


@dataclass
class ListUserBusinessesCommand:
    user_id: UUID
    page: int
    page_size: int


@dataclass
class UserBusinessResult:
    business_id: UUID
    business_name: str | None
    business_code: str | None
    roles: list[str]
    is_active: bool
    created_at: str | None


class ListUserBusinessesUseCase:
    def __init__(self, business_user_repo: IBusinessUserRepository):
        self.business_user_repo = business_user_repo

    async def execute(self, command: ListUserBusinessesCommand) -> tuple[list[UserBusinessResult], int]:
        items, total = await self.business_user_repo.list_paginated_by_user(
            user_id=command.user_id,
            page=command.page,
            page_size=command.page_size,
        )

        results = [
            UserBusinessResult(
                business_id=i.business_id,
                business_name=i.business_name,
                business_code=i.business_code,
                roles=[r.value for r in i.roles],
                is_active=i.is_active,
                created_at=i.created_at.isoformat() if i.created_at else None,
            )
            for i in items
        ]

        return results, total
