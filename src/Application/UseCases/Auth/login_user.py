import uuid
from dataclasses import dataclass

from src.Application.Exceptions.business_exceptions import UserNotFoundError
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService
from src.Domain.Ports.Services.i_token_service import ITokenService


@dataclass
class LoginUserCommand:
    email: str
    plain_password: str


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str


class InvalidCredentialsError(UserNotFoundError):
    def __init__(self):
        super().__init__("Correo o contraseña incorrectos")


class LoginUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        password_service: IPasswordHashingService,
        token_service: ITokenService,
    ):
        self._user_repo = user_repo
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, command: LoginUserCommand) -> LoginResult:
        user = await self._user_repo.get_by_email(command.email)
        
        if not user or not user.is_active:
            raise InvalidCredentialsError()

        if not self._password_service.verify(command.plain_password, user.hashed_password):
            raise InvalidCredentialsError()

        # Generar tokens
        access_token = self._token_service.create_access_token(user_id=user.id)
        
        # JTI es un identificador único para el refresh token que permite revocarlo
        jti = uuid.uuid4()
        refresh_token = self._token_service.create_refresh_token(user_id=user.id, jti=jti)

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token
        )
