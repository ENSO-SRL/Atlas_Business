import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import EmailAlreadyInUseError
from src.Domain.Entities.user import User
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService


@dataclass
class RegisterUserCommand:
    first_name: str
    last_name: str
    email: str
    plain_password: str
    phone: str | None = None


@dataclass
class RegisterUserResult:
    user_id: UUID
    email: str


class RegisterUserUseCase:
    """
    Registro inicial de un usuario en la plataforma (User global).
    Esta es la primera acción antes de poder crear un negocio o ser invitado a uno.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        password_service: IPasswordHashingService,
    ):
        self.user_repo = user_repo
        self.password_service = password_service

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        if await self.user_repo.exists_by_email(command.email):
            raise EmailAlreadyInUseError(command.email)

        try:
            user_id = uuid.uuid7()
        except AttributeError:
            user_id = uuid.uuid4()

        hashed_password = self.password_service.hash(command.plain_password)

        user = User(
            id=user_id,
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            phone=command.phone,
            hashed_password=hashed_password,
            is_active=True,
        )

        await self.user_repo.create(user)

        return RegisterUserResult(
            user_id=user.id,
            email=user.email,
        )
