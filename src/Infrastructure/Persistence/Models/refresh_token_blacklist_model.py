from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Persistence.database import Base


class RefreshTokenBlacklistModel(Base):
    __tablename__ = "refresh_token_blacklist"
    
    jti: Mapped[UUID] = mapped_column(sa.Uuid(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
