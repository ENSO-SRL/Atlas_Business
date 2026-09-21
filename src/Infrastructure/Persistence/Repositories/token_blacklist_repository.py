from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.Domain.Ports.Repositories.i_token_blacklist_repository import ITokenBlacklistRepository
from src.Infrastructure.Persistence.Models.refresh_token_blacklist_model import RefreshTokenBlacklistModel


class TokenBlacklistRepository(ITokenBlacklistRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def is_revoked(self, jti: UUID) -> bool:
        stmt = select(RefreshTokenBlacklistModel).where(RefreshTokenBlacklistModel.jti == jti)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def revoke(self, jti: UUID, user_id: UUID, expires_at: datetime) -> None:
        model = RefreshTokenBlacklistModel(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at
        )
        self._session.add(model)
        await self._session.flush()
