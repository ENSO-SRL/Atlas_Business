from dataclasses import dataclass
from uuid import UUID

from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository


@dataclass
class ListBusinessCustomersCommand:
    business_id: UUID
    page: int
    page_size: int


@dataclass
class BusinessCustomerResult:
    id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str | None
    gender: str | None
    created_at: str | None


class ListBusinessCustomersUseCase:
    def __init__(self, customer_repo: IBusinessCustomerRepository):
        self.customer_repo = customer_repo

    async def execute(self, command: ListBusinessCustomersCommand) -> tuple[list[BusinessCustomerResult], int]:
        customers, total = await self.customer_repo.list_paginated_by_business(
            business_id=command.business_id,
            page=command.page,
            page_size=command.page_size
        )

        results = [
            BusinessCustomerResult(
                id=c.id,
                first_name=c.first_name,
                last_name=c.last_name,
                phone=c.phone,
                email=c.email,
                gender=c.gender.value if c.gender else None,
                created_at=c.created_at.isoformat() if c.created_at else None,
            )
            for c in customers
        ]

        return results, total
