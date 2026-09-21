import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.Application.Exceptions.business_exceptions import EmailAlreadyVerifiedError, UserNotFoundError
from src.Domain.Entities.email_token import EmailToken, EmailTokenType
from src.Domain.Ports.Repositories.i_email_token_repository import IEmailTokenRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Services.i_email_service import IEmailService


@dataclass
class RequestEmailConfirmationCommand:
    user_id: uuid.UUID


class RequestEmailConfirmationUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        email_token_repo: IEmailTokenRepository,
        email_service: IEmailService,
    ):
        self._user_repo = user_repo
        self._email_token_repo = email_token_repo
        self._email_service = email_service

    async def execute(self, command: RequestEmailConfirmationCommand) -> None:
        user = await self._user_repo.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundError()

        if user.is_email_verified:
            raise EmailAlreadyVerifiedError()

        # Generar token de expiración de 24 horas
        try:
            token_id = uuid.uuid7()
        except AttributeError:
            token_id = uuid.uuid4()
            
        token_val = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        email_token = EmailToken(
            id=token_id,
            user_id=user.id,
            token=token_val,
            token_type=EmailTokenType.EMAIL_CONFIRMATION,
            expires_at=expires_at,
        )

        await self._email_token_repo.create(email_token)
        await self._email_service.send_email_confirmation(to_email=user.email, token=str(token_val))
