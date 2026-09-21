from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository


@dataclass
class ListBusinessUsersCommand:
    business_id: UUID


@dataclass
class BusinessUserResult:
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    roles: list[str]
    is_active: bool


class ListBusinessUsersUseCase:
    """
    Obtiene la lista de usuarios asociados a un negocio.
    """

    def __init__(self, user_repo: IBusinessUserRepository):
        self.user_repo = user_repo

    async def execute(self, command: ListBusinessUsersCommand) -> list[BusinessUserResult]:
        users = await self.user_repo.list_by_business(command.business_id)
        return [
            BusinessUserResult(
                id=u.id,
                user_id=u.user_id,
                first_name=u.user.first_name if u.user else "",
                last_name=u.user.last_name if u.user else "",
                email=u.user.email if u.user else "",
                phone=u.user.phone if u.user else None,
                roles=[r.value for r in u.roles],
                is_active=u.is_active,
            )
            for u in users
        ]
