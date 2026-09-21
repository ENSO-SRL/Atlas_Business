from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Persistence.database import Base


class EmailTokenModel(Base):
    __tablename__ = "email_token"
    
    id: Mapped[UUID] = mapped_column(sa.Uuid(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[UUID] = mapped_column(sa.Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    token_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
