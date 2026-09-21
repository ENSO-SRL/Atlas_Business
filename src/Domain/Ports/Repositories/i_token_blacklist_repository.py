from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class ITokenBlacklistRepository(ABC):
    @abstractmethod
    async def is_revoked(self, jti: UUID) -> bool:
        pass

    @abstractmethod
    async def revoke(self, jti: UUID, user_id: UUID, expires_at: datetime) -> None:
        pass
