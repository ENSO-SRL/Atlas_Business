from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import InvalidEmailTokenError, UserNotFoundError
from src.Domain.Entities.email_token import EmailTokenType
from src.Domain.Ports.Repositories.i_email_token_repository import IEmailTokenRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService


@dataclass
class ResetPasswordCommand:
    token: UUID
    new_password: str


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        email_token_repo: IEmailTokenRepository,
        password_service: IPasswordHashingService,
    ):
        self._user_repo = user_repo
        self._email_token_repo = email_token_repo
        self._password_service = password_service

    async def execute(self, command: ResetPasswordCommand) -> None:
        email_token = await self._email_token_repo.get_valid_by_token(
            token=command.token, token_type=EmailTokenType.PASSWORD_RESET
        )

        if not email_token:
            raise InvalidEmailTokenError()

        user = await self._user_repo.get_by_id(email_token.user_id)
        if not user or not user.is_active:
            raise UserNotFoundError()

        # Update password
        user.hashed_password = self._password_service.hash(command.new_password)
        await self._user_repo.update(user)

        # Invalidate token
        await self._email_token_repo.mark_as_used(email_token.id)
