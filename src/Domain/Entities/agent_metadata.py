from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass
class AgentMetadata:
    """
    Metadata del agente (presentación narrativa, políticas y requisitos)
    vinculada 1:1 a un Business o un Service.
    """
    id: UUID
    description: str
    establishment_policies: list[str] = field(default_factory=list)
    pre_booking_requirements: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None

    def __post_init__(self):
        if not self.description or not self.description.strip():
            raise ValueError("La descripción no puede estar vacía.")
