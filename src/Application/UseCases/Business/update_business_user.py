from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import UserNotFoundError
from src.Application.UseCases.Business.list_business_users import BusinessUserResult
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository


@dataclass
class UpdateBusinessUserCommand:
    business_id: UUID
    user_id: UUID
    actor_id: UUID
    roles: list[str] | None = None
    is_active: bool | None = None


class UpdateBusinessUserUseCase:
    """
    Actualiza los roles o el estado activo de un BusinessUser.
    """

    def __init__(self, user_repo: IBusinessUserRepository):
        self.user_repo = user_repo

    async def execute(self, command: UpdateBusinessUserCommand) -> BusinessUserResult:
        user = await self.user_repo.get_by_id(command.user_id, command.business_id)
        if not user:
            raise UserNotFoundError()

        changed = False
        if command.roles is not None:
            user.roles = [SystemRole(r) for r in command.roles]
            changed = True
        
        if command.is_active is not None:
            user.is_active = command.is_active
            changed = True

        if changed:
            user.updated_at = datetime.now(timezone.utc)
            user.updated_by = command.actor_id
            await self.user_repo.update(user)

        return BusinessUserResult(
            id=user.id,
            user_id=user.user_id,
            first_name=user.user.first_name if user.user else "",
            last_name=user.user.last_name if user.user else "",
            email=user.user.email if user.user else "",
            phone=user.user.phone if user.user else None,
            roles=[r.value for r in user.roles],
            is_active=user.is_active,
        )
