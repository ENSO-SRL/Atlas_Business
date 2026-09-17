from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


class BookableObjectModel(Base):
    """
    Modelo ORM para la tabla bookable_object.
    Recurso físico concreto (cancha, mesa, sala) que puede ser asignado a una reserva.
    """
    __tablename__ = "bookable_object"

    __table_args__ = (
        # Filtro principal: objetos activos de un servicio.
        sa.Index("ix_bookable_object_service_active", "service_id", "is_active"),
        # Filtro de capacidad usado en el cálculo de disponibilidad.
        sa.Index("ix_bookable_object_capacity", "service_id", "min_capacity", "max_capacity"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    service_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Puede ser None para servicios donde el objeto no tiene identidad visible (ej. Golf).
    name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    min_capacity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    max_capacity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.true())

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    service = relationship("ServiceModel", back_populates="bookable_objects", lazy="select")
    bookings = relationship("BookingModel", back_populates="bookable_object", lazy="select")
