from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


class BusinessUserModel(Base):
    """
    Modelo ORM para la tabla business_user.
    Relación entre un User y un Business con sus roles.
    """
    __tablename__ = "business_user"

    __table_args__ = (
        # Un User solo puede aparecer 1 vez por Business
        sa.UniqueConstraint("user_id", "business_id", name="uq_business_user_membership"),
        sa.Index("ix_business_user_business_id", "business_id"),
        sa.Index("ix_business_user_user_id", "user_id"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), 
        sa.ForeignKey("user.id"), 
        nullable=False
    )
    business_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Lista de strings almacenada como JSONB. Ej: ["ADMIN"] o ["RECEPTIONIST"].
    roles: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.true())

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    user = relationship("UserModel", back_populates="business_memberships", lazy="select")
    business = relationship("BusinessModel", back_populates="users", lazy="select")
