from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import InvalidEmailTokenError, UserNotFoundError
from src.Domain.Entities.email_token import EmailTokenType
from src.Domain.Ports.Repositories.i_email_token_repository import IEmailTokenRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository


@dataclass
class ConfirmEmailCommand:
    token: UUID


class ConfirmEmailUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        email_token_repo: IEmailTokenRepository,
    ):
        self._user_repo = user_repo
        self._email_token_repo = email_token_repo

    async def execute(self, command: ConfirmEmailCommand) -> None:
        email_token = await self._email_token_repo.get_valid_by_token(
            token=command.token, token_type=EmailTokenType.EMAIL_CONFIRMATION
        )

        if not email_token:
            raise InvalidEmailTokenError()

        user = await self._user_repo.get_by_id(email_token.user_id)
        if not user:
            raise UserNotFoundError()

        # Update user
        user.is_email_verified = True
        await self._user_repo.update(user)

        # Invalidate token
        await self._email_token_repo.mark_as_used(email_token.id)
