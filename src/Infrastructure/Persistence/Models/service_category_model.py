from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Persistence.database import Base


class ServiceCategoryModel(Base):
    __tablename__ = "service_category"

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.true())
    is_deleted: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.false())
