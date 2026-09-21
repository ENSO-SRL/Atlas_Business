from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Entities.email_token import EmailToken, EmailTokenType
from src.Domain.Ports.Repositories.i_email_token_repository import IEmailTokenRepository
from src.Infrastructure.Persistence.Models.email_token_model import EmailTokenModel


class EmailTokenRepository(IEmailTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: EmailTokenModel) -> EmailToken:
        return EmailToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            token_type=EmailTokenType(model.token_type),
            expires_at=model.expires_at,
            used_at=model.used_at,
        )

    async def create(self, entity: EmailToken) -> None:
        model = EmailTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token=entity.token,
            token_type=entity.token_type.value,
            expires_at=entity.expires_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def get_valid_by_token(self, token: UUID, token_type: EmailTokenType) -> EmailToken | None:
        now = datetime.now(timezone.utc)
        stmt = select(EmailTokenModel).where(
            EmailTokenModel.token == token,
            EmailTokenModel.token_type == token_type.value,
            EmailTokenModel.used_at.is_(None),
            EmailTokenModel.expires_at > now
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def mark_as_used(self, token_id: UUID) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(EmailTokenModel)
            .where(EmailTokenModel.id == token_id)
            .values(used_at=now)
        )
        await self._session.execute(stmt)
        await self._session.flush()
