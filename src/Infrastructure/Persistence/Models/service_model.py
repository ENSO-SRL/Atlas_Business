from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base

# Enums nativos de PostgreSQL.
_duration_nature_enum = sa.Enum(
    "FIXED", "ESTIMATED", "INSTANT",
    name="duration_nature_enum",
    create_type=True,
)

_billing_nature_enum = sa.Enum(
    "BILLABLE", "NON_BILLABLE",
    name="billing_nature_enum",
    create_type=True,
)

_auto_selection_enum = sa.Enum(
    "CLOSEST_MAX_CAPACITY",
    name="auto_selection_enum",
    create_type=True,
)

_publication_status_enum = sa.Enum(
    "DRAFT", "PUBLISHED", "UNDER_REVIEW", "REJECTED",
    name="publication_status_enum",
    create_type=True,
)


class ServiceModel(Base):
    """
    Modelo ORM para la tabla service.
    Unidad reservable con su configuración operativa y estado de publicación.
    """
    __tablename__ = "service"

    __table_args__ = (
        # Filtro más frecuente: servicios publicados de un negocio.
        sa.Index("ix_service_business_publication", "business_id", "publication_status"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    occupation_duration_minutes: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    duration_nature: Mapped[str] = mapped_column(_duration_nature_enum, nullable=False)
    exposes_end_time: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    buffer_minutes: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")
    grid_interval_minutes: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    max_booking_window_days: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="30")
    min_booking_window_hours: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="2")
    max_daily_bookings_per_user: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="1")
    allows_manual_object_selection: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    auto_selection_criteria: Mapped[str] = mapped_column(_auto_selection_enum, nullable=False)
    billing_nature: Mapped[str] = mapped_column(_billing_nature_enum, nullable=False)
    agent_metadata_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("agent_metadata.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("service_category.id", ondelete="RESTRICT"),
        nullable=False,
    )
    publication_status: Mapped[str] = mapped_column(
        _publication_status_enum,
        nullable=False,
        server_default="DRAFT",
    )
    # Motivo de rechazo en la moderación de creación. Nulo si no fue rechazado.
    rejection_reason: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    
    vertical_metadata: Mapped[dict] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'{}'::jsonb")
    )

    # Políticas de Servicio (Payment & Cancellation)
    payment_splits: Mapped[list[dict] | None] = mapped_column(sa.dialects.postgresql.JSONB, nullable=True)
    cancellation_description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    min_cancellation_margin_hours: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    cancellation_fee: Mapped[float | None] = mapped_column(sa.Numeric(10, 2), nullable=True)

    # Políticas de Servicio (Modification)
    allows_same_day_reschedule: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    allows_date_change: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)
    date_change_margin_days: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    # Políticas de Servicio (Arrival)
    wait_time_minutes: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    release_automatically: Mapped[bool | None] = mapped_column(sa.Boolean, nullable=True)

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)

    # Relaciones ORM
    business = relationship("BusinessModel", back_populates="services", lazy="select")
    agent_metadata = relationship("AgentMetadataModel", foreign_keys=[agent_metadata_id], lazy="select")
    bookable_objects = relationship("BookableObjectModel", back_populates="service", lazy="select")
    rates = relationship("ServiceRateModel", back_populates="service", lazy="select")
    bookings = relationship("BookingModel", back_populates="service", lazy="select")
    custom_fields = relationship("CustomFieldModel", back_populates="service", lazy="select")
    content_requests = relationship("ContentRequestModel", back_populates="service", lazy="select")
