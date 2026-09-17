from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base

_content_request_status_enum = sa.Enum(
    "PENDING_FILTER", "APPROVED", "UNDER_REVIEW", "REJECTED", "SUPERSEDED",
    name="content_request_status_enum",
    create_type=True,
)


class ContentRequestModel(Base):
    """
    Modelo ORM para la tabla content_request.
    Solicitud de edición sobre un Service ya publicado (patrón shadow edit).
    La versión publicada del servicio queda intacta mientras la solicitud está pendiente.

    Hay como máximo 1 solicitud activa (PENDING_FILTER o UNDER_REVIEW) por servicio.
    Una nueva edición marca la solicitud anterior como SUPERSEDED.
    """
    __tablename__ = "content_request"

    __table_args__ = (
        # Consulta normal: solicitud más reciente de un servicio.
        sa.Index("ix_content_request_service_status", "service_id", "status"),
        # Partial index muy selectivo para encontrar la solicitud activa de un servicio.
        # En la práctica hay 0 o 1 filas por service_id en este índice.
        sa.Index(
            "ix_content_request_active",
            "service_id",
            postgresql_where=sa.text("status IN ('PENDING_FILTER', 'UNDER_REVIEW')"),
        ),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    service_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        _content_request_status_enum,
        nullable=False,
        server_default="PENDING_FILTER",
    )
    # Diff de los campos que cambiaron. Nunca vacío — una solicitud siempre tiene cambios.
    payload: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    # Campos de texto libre que dispararon el filtro de contenido.
    filter_matches: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    # Requerido cuando status == REJECTED.
    rejection_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    # UUID del revisor del equipo interno. Sin FK — el revisor no es un BusinessUser.
    reviewed_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)

    # Campos de auditoría (created_by = UUID del BusinessUser que originó la edición)
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    service = relationship("ServiceModel", back_populates="content_requests", lazy="select")
