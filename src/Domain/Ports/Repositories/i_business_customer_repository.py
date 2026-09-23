from abc import ABC, abstractmethod
from uuid import UUID

from src.Domain.Entities.business_customer import BusinessCustomer


class IBusinessCustomerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID, business_id: UUID) -> BusinessCustomer | None:
        ...

    @abstractmethod
    async def get_by_phone(self, phone: str, business_id: UUID) -> BusinessCustomer | None:
        ...

    @abstractmethod
    async def list_paginated_by_business(
        self, business_id: UUID, page: int, page_size: int
    ) -> tuple[list[BusinessCustomer], int]:
        ...

    @abstractmethod
    async def create(self, entity: BusinessCustomer) -> BusinessCustomer:
        ...

    @abstractmethod
    async def update(self, entity: BusinessCustomer) -> BusinessCustomer:
        ...
