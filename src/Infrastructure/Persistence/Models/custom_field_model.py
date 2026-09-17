from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base

_data_type_enum = sa.Enum(
    "SHORT_TEXT", "LONG_TEXT", "NUMBER",
    "SINGLE_CHOICE", "MULTI_CHOICE",
    "YES_NO", "DATE",
    name="data_type_enum",
    create_type=True,
)


class CustomFieldModel(Base):
    """
    Modelo ORM para la tabla custom_field.
    Define campos adicionales tipados para un servicio o negocio.
    No almacena valores — las respuestas viven en booking.custom_fields (JSONB).
    """
    __tablename__ = "custom_field"

    __table_args__ = (
        # Recuperar campos de un servicio específico o del negocio en general.
        sa.Index("ix_custom_field_business_service", "business_id", "service_id"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Nullable: si es None, el campo pertenece al negocio en general (no a un servicio).
    service_id: Mapped[UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service.id", ondelete="CASCADE"),
        nullable=True,
    )
    label: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    # Instrucción interna para el agente — no se expone al cliente final.
    agent_note: Mapped[str] = mapped_column(sa.Text, nullable=False)
    # Orden de presentación dentro del formulario.
    order: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    required: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    visible_to_client: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    data_type: Mapped[str] = mapped_column(_data_type_enum, nullable=False)
    # Solo para SINGLE_CHOICE y MULTI_CHOICE. Null en todos los demás tipos.
    options: Mapped[list | None] = mapped_column(sa.JSON, nullable=True)
    # Solo para NUMBER — define rango válido. Null en todos los demás tipos.
    minimum: Mapped[float | None] = mapped_column(sa.Float, nullable=True)
    maximum: Mapped[float | None] = mapped_column(sa.Float, nullable=True)

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    business = relationship("BusinessModel", back_populates="custom_fields", lazy="select")
    service = relationship("ServiceModel", back_populates="custom_fields", lazy="select")
