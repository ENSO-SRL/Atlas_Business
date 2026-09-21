from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.email_token import EmailToken, EmailTokenType


class IEmailTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: EmailToken) -> None:
        pass

    @abstractmethod
    async def get_valid_by_token(self, token: UUID, token_type: EmailTokenType) -> EmailToken | None:
        pass

    @abstractmethod
    async def mark_as_used(self, token_id: UUID) -> None:
        pass
