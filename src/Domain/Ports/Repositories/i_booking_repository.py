from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.Domain.Entities.booking import Booking


class IBookingRepository(ABC):
    @abstractmethod
    async def list_by_business(
        self,
        business_id: UUID,
        service_id: UUID | None = None,
        filter_date: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Booking], int]:
        """
        Devuelve (items, total) para paginación.
        """
        ...

    @abstractmethod
    async def get_by_id(self, id: UUID, business_id: UUID) -> Booking | None:
        ...

    @abstractmethod
    async def list_by_customer(
        self,
        customer_id: UUID,
        business_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Booking], int]:
        ...
