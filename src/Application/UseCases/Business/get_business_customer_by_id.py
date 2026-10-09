from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import CustomerNotFoundError
from src.Domain.Entities.business_customer import BusinessCustomer
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository


@dataclass
class GetBusinessCustomerByIdCommand:
    business_id: UUID
    customer_id: UUID


class GetBusinessCustomerByIdUseCase:
    def __init__(self, customer_repo: IBusinessCustomerRepository):
        self.customer_repo = customer_repo

    async def execute(self, command: GetBusinessCustomerByIdCommand) -> BusinessCustomer:
        customer = await self.customer_repo.get_by_id(command.customer_id, command.business_id)
        if not customer:
            raise CustomerNotFoundError()
        return customer
