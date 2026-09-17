from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository


@dataclass
class ListBusinessUsersCommand:
    business_id: UUID


@dataclass
class BusinessUserResult:
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: list[str]
    is_active: bool


class ListBusinessUsersUseCase:
    """
    Lista los BusinessUser de un negocio.
    """

    def __init__(self, user_repo: IBusinessUserRepository):
        self.user_repo = user_repo

    async def execute(self, command: ListBusinessUsersCommand) -> list[BusinessUserResult]:
        users = await self.user_repo.list_by_business(command.business_id)

        return [
            BusinessUserResult(
                id=u.id,
                first_name=u.first_name,
                last_name=u.last_name,
                email=u.email,
                phone=u.phone,
                roles=[r.value for r in u.roles],
                is_active=u.is_active,
            )
            for u in users
        ]
