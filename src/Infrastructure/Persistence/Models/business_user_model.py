from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


class BusinessUserModel(Base):
    """
    Modelo ORM para la tabla business_user.
    Usuario afiliado a un negocio con uno o más roles del sistema.
    """
    __tablename__ = "business_user"

    __table_args__ = (
        # El email es único dentro del contexto de un negocio, no globalmente.
        sa.UniqueConstraint("business_id", "email", name="uq_business_user_email"),
        sa.Index("ix_business_user_business_id", "business_id"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(sa.String(30), nullable=True)
    hashed_password: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Lista de strings almacenada como JSONB. Ej: ["ADMIN"] o ["RECEPTIONIST"].
    # Descartamos tabla de relación normalizada — roles son simples en el MVP.
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
    business = relationship("BusinessModel", back_populates="users", lazy="select")
