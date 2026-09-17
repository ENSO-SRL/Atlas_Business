from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Persistence.database import Base


class AgentMetadataModel(Base):
    """
    Modelo ORM para la tabla agent_metadata.
    Almacena el contenido narrativo inyectado en el agente de IA para un negocio o servicio.
    """
    __tablename__ = "agent_metadata"

    id: Mapped[UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)

    # Listas de strings almacenadas como JSONB — siempre se leen completas, nunca se filtran por elemento.
    establishment_policies: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    pre_booking_requirements: Mapped[list] = mapped_column(
        sa.JSON, nullable=False, server_default=sa.text("'[]'::jsonb")
    )

    # Campos de auditoría
    created_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
