from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base

_calculation_basis_enum = sa.Enum(
    "PER_BOOKING", "PER_PERSON",
    name="calculation_basis_enum",
    create_type=True,
)


class ServiceRateModel(Base):
    """
    Modelo ORM para la tabla service_rate.
    Define el precio de un servicio según día de la semana y franja horaria.
    El conjunto completo de tarifas de un servicio cubre el horario laboral sin huecos.
    """
    __tablename__ = "service_rate"

    __table_args__ = (
        sa.Index("ix_service_rate_service_id", "service_id"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    service_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Lista de strings JSONB: ["MONDAY", "TUESDAY", ...].
    # Nunca se filtra por día individual en SQL — se lee el set completo y se evalúa en Python.
    weekdays: Mapped[list] = mapped_column(sa.JSON, nullable=False)
    start_time: Mapped[time] = mapped_column(sa.Time, nullable=False)
    end_time: Mapped[time] = mapped_column(sa.Time, nullable=False)
    # NUMERIC(12,2) para aritmética exacta de dinero. Nunca usar FLOAT para montos.
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    calculation_basis: Mapped[str] = mapped_column(_calculation_basis_enum, nullable=False)

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    service = relationship("ServiceModel", back_populates="rates", lazy="select")
