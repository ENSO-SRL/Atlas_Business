from src.Domain.Enums.weekday import Weekday
from src.Domain.Entities.business import BusinessSchedule
from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import BusinessCodeAlreadyExistsError, InvalidRncError, BusinessCategoryNotFoundError
from src.Domain.Entities.agent_metadata import AgentMetadata
from src.Domain.Entities.business import Business
from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Enums.platform import Platform
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Enums.verification_status import VerificationStatus
from src.Domain.Ports.Repositories.i_agent_metadata_repository import IAgentMetadataRepository
from src.Domain.Ports.Repositories.i_business_category_repository import IBusinessCategoryRepository
from src.Domain.Ports.Repositories.i_business_repository import IBusinessRepository
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Services.i_rnc_validation_service import IRncValidationService
from src.Domain.Ports.Services.i_content_filter_service import IContentFilterService
import uuid


@dataclass
class ScheduleInput:
    weekday: str
    opening_time: str
    closing_time: str


@dataclass
class RegisterBusinessCommand:
    # ID del User autenticado que crea el negocio
    owner_user_id: UUID
    # Datos del negocio
    code: str
    name: str
    #category: str
    platform: str
    address: str
    phone: str
    rnc: str
    category_id: uuid.UUID
    maps_url: str | None
    aliases: list[str]
    schedules: list[ScheduleInput]
    # Metadata del agente para el negocio
    description: str
    establishment_policies: list[str]
    pre_booking_requirements: list[str]


@dataclass
class RegisterBusinessResult:
    business_id: UUID
    business_code: str
    message: str


class RegisterBusinessUseCase:
    """
    Registro inicial de un negocio. 
    El usuario que lo crea (ya autenticado y existente en el sistema) 
    se asigna automáticamente como OWNER de dicho negocio.
    """

    def __init__(
        self,
        business_repo: IBusinessRepository,
        agent_metadata_repo: IAgentMetadataRepository,
        business_user_repo: IBusinessUserRepository,
        rnc_service: IRncValidationService,
        content_filter: IContentFilterService,
        business_category_repo: IBusinessCategoryRepository,
    ):
        self.business_repo = business_repo
        self.agent_metadata_repo = agent_metadata_repo
        self.business_user_repo = business_user_repo
        self.rnc_service = rnc_service
        self.content_filter = content_filter
        self.business_category_repo = business_category_repo

    async def execute(self, command: RegisterBusinessCommand) -> RegisterBusinessResult:
        # 1. Verificar unicidad de código
        existing_business = await self.business_repo.get_by_code(command.code)
        if existing_business:
            raise BusinessCodeAlreadyExistsError(command.code)

        # 2. Validar RNC contra la DGII (o mock)
        rnc_is_valid = await self.rnc_service.validate(command.rnc)
        if not rnc_is_valid:
            raise InvalidRncError(command.rnc)

        # 3. Validar categoría de negocio
        category = await self.business_category_repo.get_by_id(command.category_id)
        if not category or not category.is_active:
            raise BusinessCategoryNotFoundError()

        # 2. Crear AgentMetadata
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

        # 3. Filtrar contenido
        matches = await self.content_filter.check({
            "name": command.name,
            "description": command.description,
            "aliases": ", ".join(command.aliases),
            "establishment_policies": "\n".join(command.establishment_policies),
            "pre_booking_requirements": "\n".join(command.pre_booking_requirements),
        })

        initial_status = VerificationStatus.PENDING_VERIFICATION if matches else VerificationStatus.VERIFIED
        message = "En revisión por posible contenido restringido." if matches else "Negocio publicado exitosamente."

        # 4. Crear Business
        try:
            business_id = uuid.uuid7()
        except AttributeError:
            business_id = uuid.uuid4()

        schedules = [
            BusinessSchedule(
                weekday=Weekday(s.weekday),
                opening_time=s.opening_time,
                closing_time=s.closing_time,
            )
            for s in command.schedules
        ]
        
        business = Business(
            id=business_id,
            code=command.code,
            name=command.name,
            rnc=command.rnc,
            category_id=command.category_id,
            platform=Platform(command.platform),
            verification_status=initial_status,
            address=command.address,
            maps_url=command.maps_url,
            phone=command.phone,
            aliases=command.aliases,
            schedules=schedules,
            agent_metadata_id=metadata_id,
        )
        await self.business_repo.create(business)

        # 4. Vincular al Owner
        try:
            business_user_id = uuid.uuid7()
        except AttributeError:
            business_user_id = uuid.uuid4()

        owner_link = BusinessUser(
            id=business_user_id,
            user_id=command.owner_user_id,
            business_id=business_id,
            roles=[SystemRole.OWNER],
            is_active=True,
            created_by=command.owner_user_id,
        )
        await self.business_user_repo.create(owner_link)

        return RegisterBusinessResult(
            business_id=business_id,
            business_code=command.code,
            message=message,
        )
