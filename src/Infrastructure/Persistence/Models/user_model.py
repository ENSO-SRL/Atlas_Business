from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


class UserModel(Base):
    """
    Modelo ORM para la tabla user.
    Entidad de identidad. Email único global.
    """
    __tablename__ = "user"

    __table_args__ = (
        sa.UniqueConstraint("email", name="uq_user_email_global"),
        sa.Index("ix_user_email", "email"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    first_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(sa.String(30), nullable=True)
    hashed_password: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.true())
    
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)

    # Relación inversa
    business_memberships = relationship("BusinessUserModel", back_populates="user", lazy="select")
