import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import EmailAlreadyInUseError
from src.Application.UseCases.Business.list_business_users import BusinessUserResult
from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService


@dataclass
class CreateBusinessUserCommand:
    business_id: UUID
    actor_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    plain_password: str
    roles: list[str]


class CreateBusinessUserUseCase:
    """
    Crea un nuevo usuario para el negocio, validando unicidad de email.
    """

    def __init__(
        self,
        user_repo: IBusinessUserRepository,
        password_service: IPasswordHashingService,
    ):
        self.user_repo = user_repo
        self.password_service = password_service

    async def execute(self, command: CreateBusinessUserCommand) -> BusinessUserResult:
        existing_user = await self.user_repo.get_by_email(command.email, command.business_id)
        if existing_user:
            raise EmailAlreadyInUseError(command.email)

        try:
            user_id = uuid.uuid7()
        except AttributeError:
            user_id = uuid.uuid4()

        hashed_password = self.password_service.hash(command.plain_password)
        roles = [SystemRole(r) for r in command.roles]

        user = BusinessUser(
            id=user_id,
            business_id=command.business_id,
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            phone=command.phone,
            hashed_password=hashed_password,
            roles=roles,
            is_active=True,
            created_by=command.actor_id,
        )

        await self.user_repo.create(user)

        return BusinessUserResult(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            roles=[r.value for r in user.roles],
            is_active=user.is_active,
        )
