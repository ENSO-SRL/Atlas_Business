from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BusinessCodeAlreadyExistsError
from src.Domain.Entities.agent_metadata import AgentMetadata
from src.Domain.Entities.business import Business
from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Enums.platform import Platform
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService
import uuid


@dataclass
class ScheduleInput:
    weekday: str
    opening_time: str
    closing_time: str


@dataclass
class RegisterBusinessCommand:
    # Datos del negocio
    code: str
    name: str
    category: str
    platform: str
    address: str
    phone: str
    maps_url: str | None
    aliases: list[str]
    schedules: list[ScheduleInput]
    # Metadata del agente para el negocio
    description: str
    establishment_policies: list[str]
    pre_booking_requirements: list[str]
    # Datos del administrador inicial
    admin_first_name: str
    admin_last_name: str
    admin_email: str
    admin_phone: str | None
    admin_password: str


@dataclass
class RegisterBusinessResult:
    business_id: UUID
    business_code: str
    admin_user_id: UUID


class RegisterBusinessUseCase:
    """
    Registro inicial de un negocio junto con su usuario administrador base.
    Ambas entidades se crean en una sola operación coordinada.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        user_repo: IBusinessUserRepository,
        password_service: IPasswordHashingService,
    ):
        self.business_repo = business_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.user_repo = user_repo
        self.password_service = password_service

    async def execute(self, command: RegisterBusinessCommand) -> RegisterBusinessResult:
        # 1. Verificar unicidad de código
        existing_business = await self.business_repo.get_by_code(command.code)
        if existing_business:
            raise BusinessCodeAlreadyExistsError(command.code)

        # 2. Crear AgentMetadata
        # Python 3.12+ (uuid7)
        try:
            metadata_id = uuid.uuid7()
        except AttributeError:
            metadata_id = uuid.uuid4()
            
        metadata = AgentMetadata(
            id=metadata_id,
            description=command.description,
            establishment_policies=command.establishment_policies,
            pre_booking_requirements=command.pre_booking_requirements,
        )
        await self.agent_metadata_repo.create(metadata)

        # 3. Crear Business
        try:
            business_id = uuid.uuid7()
        except AttributeError:
            business_id = uuid.uuid4()

        schedules = [
            {"weekday": s.weekday, "opening_time": s.opening_time, "closing_time": s.closing_time}
            for s in command.schedules
        ]
        
        business = Business(
            id=business_id,
            code=command.code,
            name=command.name,
            category=command.category,
            platform=Platform(command.platform),
            verification_status=VerificationStatus.PENDING_VERIFICATION,
            address=command.address,
            maps_url=command.maps_url,
            phone=command.phone,
            aliases=command.aliases,
            schedules=schedules,
            agent_metadata_id=metadata_id,
        )
        await self.business_repo.create(business)

        # 4. Crear Admin User
        try:
            user_id = uuid.uuid7()
        except AttributeError:
            user_id = uuid.uuid4()
            
        hashed_password = self.password_service.hash(command.admin_password)

        admin_user = BusinessUser(
            id=user_id,
            business_id=business_id,
            first_name=command.admin_first_name,
            last_name=command.admin_last_name,
            email=command.admin_email,
            phone=command.admin_phone,
            hashed_password=hashed_password,
            roles=[SystemRole.ADMIN],
            is_active=True,
        )
        await self.user_repo.create(admin_user)

        return RegisterBusinessResult(
            business_id=business_id,
            business_code=command.code,
            admin_user_id=user_id,
        )
