from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.service import Service


class IClientServiceRepository(ABC):
    """
    Puerto de repositorio de servicios para la Client API.
    Filtra siempre por publication_status == PUBLISHED.
    """

    @abstractmethod
    async def get_published_by_id(self, service_id: UUID, business_id: UUID) -> Service | None:
        """Obtiene un servicio publicado asegurando que pertenece al negocio dado."""
        pass

    @abstractmethod
    async def get_published_by_id_only(self, service_id: UUID) -> Service | None:
        """Obtiene un servicio publicado dado solo su ID."""
        pass

    @abstractmethod
    async def list_published_by_business(self, business_id: UUID) -> list[Service]:
        """Lista todos los servicios publicados de un negocio."""
        pass
