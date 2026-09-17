from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.service_rate import ServiceRate


class IServiceRateRepository(ABC):
    @abstractmethod
    async def list_by_service(self, service_id: UUID) -> list[ServiceRate]:
        ...

    @abstractmethod
    async def replace_all(
        self,
        service_id: UUID,
        new_rates: list[ServiceRate],
    ) -> list[ServiceRate]:
        """
        Operación atómica: elimina todas las tarifas existentes e inserta el nuevo set en una transacción.
        """
        ...
