import uuid
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, timezone

from src.Application.Exceptions.business_exceptions import CustomerAlreadyExistsError
from src.Domain.Entities.business_customer import BusinessCustomer
from src.Domain.Enums.gender import Gender
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository


@dataclass
class CreateBusinessCustomerCommand:
    business_id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str | None = None
    gender: str | None = None


@dataclass
class BusinessCustomerResult:
    id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str | None
    gender: str | None
    created_at: str | None


class CreateBusinessCustomerUseCase:
    """
    Crea un nuevo cliente para el negocio manualmente, sin usar el agente externo.
    """

    def __init__(self, customer_repo: IBusinessCustomerRepository):
        self.customer_repo = customer_repo

    async def execute(self, command: CreateBusinessCustomerCommand) -> BusinessCustomerResult:
        existing = await self.customer_repo.get_by_phone(command.phone, command.business_id)
        if existing:
            raise CustomerAlreadyExistsError(command.phone)

        try:
            new_id = uuid.uuid7()
        except AttributeError:
            new_id = uuid.uuid4()

        gender_enum = None
        if command.gender:
            try:
                gender_enum = Gender(command.gender.upper())
            except ValueError:
                pass

        new_customer = BusinessCustomer(
            id=new_id,
            business_id=command.business_id,
            first_name=command.first_name.strip(),
            last_name=command.last_name.strip(),
            phone=command.phone.strip(),
            email=command.email.strip() if command.email else None,
            gender=gender_enum,
        )

        created = await self.customer_repo.create(new_customer)
        
        created_at_str = None
        if created.created_at:
            created_at_str = created.created_at.isoformat()
        else:
            created_at_str = datetime.now(timezone.utc).isoformat()

        return BusinessCustomerResult(
            id=created.id,
            first_name=created.first_name,
            last_name=created.last_name,
            phone=created.phone,
            email=created.email,
            gender=created.gender.value if created.gender else None,
            created_at=created_at_str,
        )
