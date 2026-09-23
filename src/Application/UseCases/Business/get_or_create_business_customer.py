import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Domain.Entities.business_customer import BusinessCustomer
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository
from src.Domain.Ports.Services.i_external_agent_identity_service import IExternalAgentIdentityService


@dataclass
class GetOrCreateBusinessCustomerCommand:
    business_id: UUID
    phone: str


class GetOrCreateBusinessCustomerUseCase:
    def __init__(
        self,
        customer_repo: IBusinessCustomerRepository,
        identity_service: IExternalAgentIdentityService,
    ):
        self.customer_repo = customer_repo
        self.identity_service = identity_service

    async def execute(self, command: GetOrCreateBusinessCustomerCommand) -> BusinessCustomer:
        # 1. Buscar si ya existe el cliente en el negocio
        existing_customer = await self.customer_repo.get_by_phone(command.phone, command.business_id)
        if existing_customer:
            return existing_customer

        # 2. Consultar al servicio externo
        agent_identity = await self.identity_service.get_user_info_by_phone(command.phone)
        
        if agent_identity:
            first_name = agent_identity.first_name
            last_name = agent_identity.last_name
            email = agent_identity.email
            gender = agent_identity.gender
        else:
            # Fallback en caso de que el sistema del Agente IA no lo tenga registrado.
            # En un sistema real podría fallar aquí, o crearlo como un "guest".
            first_name = "Cliente"
            last_name = "No Registrado"
            email = None
            gender = None

        # 3. Crear y persistir
        try:
            new_id = uuid.uuid7()
        except AttributeError:
            new_id = uuid.uuid4()

        new_customer = BusinessCustomer(
            id=new_id,
            business_id=command.business_id,
            first_name=first_name,
            last_name=last_name,
            phone=command.phone,
            email=email,
            gender=gender,
        )

        return await self.customer_repo.create(new_customer)
