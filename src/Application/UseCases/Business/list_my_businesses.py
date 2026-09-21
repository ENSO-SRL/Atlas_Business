from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository


@dataclass
class ListMyBusinessesCommand:
    user_id: UUID


@dataclass
class MyBusinessItem:
    business_id: UUID
    business_name: str
    business_code: str
    roles: list[str]
    is_active: bool


class ListMyBusinessesUseCase:
    """
    Obtiene el directorio de negocios a los que pertenece un usuario.
    """

    def __init__(self, business_user_repo: IBusinessUserRepository):
        self.business_user_repo = business_user_repo

    async def execute(self, command: ListMyBusinessesCommand) -> list[MyBusinessItem]:
        links = await self.business_user_repo.list_by_user(command.user_id)
        
        return [
            MyBusinessItem(
                business_id=link.business_id,
                business_name=link.business_name or "",
                business_code=link.business_code or "",
                roles=[r.value for r in link.roles],
                is_active=link.is_active,
            )
            for link in links
        ]
