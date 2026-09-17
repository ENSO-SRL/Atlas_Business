from datetime import datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


class BookingModel(Base):
    """
    Modelo ORM para la tabla booking.
    Reserva concreta que vincula un cliente, un servicio y un objeto reservable.

    IMPORTANTE — Exclusion Constraint GiST:
    La protección definitiva contra doble reserva (race condition) vive en un exclusion
    constraint GiST que NO puede modelarse en SQLAlchemy declarativamente.
    Debe agregarse como DDL raw en la migración de Alembic:

        ALTER TABLE booking
        ADD CONSTRAINT no_overlap_per_object
        EXCLUDE USING gist (
            bookable_object_id WITH =,
            tstzrange(start_time, end_time, '[)') WITH &&
        );

    Requiere la extensión btree_gist: CREATE EXTENSION IF NOT EXISTS btree_gist;
    """
    __tablename__ = "booking"

    __table_args__ = (
        # Índice crítico para el query de disponibilidad (secc. 3 del doc de cálculo).
        # Agrupa reservas por objeto y filtra por rango de fecha.
        sa.Index("ix_booking_object_start", "bookable_object_id", "start_time"),
        # Índice para la vista de reservas del negocio filtrada por servicio y fecha.
        sa.Index("ix_booking_service_start", "service_id", "start_time"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    service_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bookable_object_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("bookable_object.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # TIMESTAMPTZ — siempre UTC en la BD, conversión a zona local en presentación.
    start_time: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=False)
    party_size: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    # Null para servicios NON_BILLABLE.
    calculated_amount: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2), nullable=True)
    # Dict libre con las respuestas a los CustomField del servicio. Llaves = UUID del campo.
    custom_fields: Mapped[dict] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'{}'::jsonb")
    )

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    service = relationship("ServiceModel", back_populates="bookings", lazy="select")
    bookable_object = relationship("BookableObjectModel", back_populates="bookings", lazy="select")
