from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base

# Enums nativos de PostgreSQL — la BD valida los valores permitidos.
_platform_enum = sa.Enum(
    "PADEL", "GOLF", "RESTAURANT",
    name="platform_enum",
    create_type=True,
)

_verification_status_enum = sa.Enum(
    "PENDING_VERIFICATION", "VERIFIED", "SUSPENDED", "REJECTED",
    name="verification_status_enum",
    create_type=True,
)


class BusinessModel(Base):
    """
    Modelo ORM para la tabla business.
    Entidad raíz del agregado. Agrupa servicios, usuarios y su estado de verificación.
    """
    __tablename__ = "business"

    __table_args__ = (
        sa.Index("ix_business_verification_status", "verification_status"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    rnc: Mapped[str] = mapped_column(sa.String(11), nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(_platform_enum, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        _verification_status_enum,
        nullable=False,
        server_default="PENDING_VERIFICATION",
    )
    address: Mapped[str] = mapped_column(sa.Text, nullable=False)
    maps_url: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    phone: Mapped[str] = mapped_column(sa.String(30), nullable=False)

    # Listas de strings almacenadas como JSONB.
    aliases: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    # Lista de objetos {weekday, opening_time, closing_time} almacenada como JSONB.
    schedules: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )

    agent_metadata_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("agent_metadata.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business_category.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    category = relationship("BusinessCategoryModel", foreign_keys=[category_id], lazy="select")
    agent_metadata = relationship("AgentMetadataModel", foreign_keys=[agent_metadata_id], lazy="select")
    services = relationship("ServiceModel", back_populates="business", lazy="select")
    users = relationship("BusinessUserModel", back_populates="business", lazy="select")
    custom_fields = relationship("CustomFieldModel", back_populates="business", lazy="select")
