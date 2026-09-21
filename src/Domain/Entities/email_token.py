from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class EmailTokenType(str, Enum):
    EMAIL_CONFIRMATION = "EMAIL_CONFIRMATION"
    PASSWORD_RESET = "PASSWORD_RESET"


@dataclass
class EmailToken:
    id: UUID
    user_id: UUID
    token: UUID
    token_type: EmailTokenType
    expires_at: datetime
    used_at: datetime | None = None
