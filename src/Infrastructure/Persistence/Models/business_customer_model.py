from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.Infrastructure.Persistence.database import Base


_gender_enum = sa.Enum(
    "MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY",
    name="gender_enum",
    create_type=False,
)

class BusinessCustomerModel(Base):
    """
    Modelo ORM para la tabla business_customer.
    """
    __tablename__ = "business_customer"

    __table_args__ = (
        sa.UniqueConstraint("business_id", "phone", name="uq_business_customer_phone"),
    )

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    business_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("business.id", ondelete="RESTRICT"),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    phone: Mapped[str] = mapped_column(sa.String(30), nullable=False)
    gender: Mapped[str | None] = mapped_column(_gender_enum, nullable=True)
    
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)

    business = relationship("BusinessModel", back_populates="customers", lazy="select")
    bookings = relationship("BookingModel", back_populates="customer", lazy="select")
