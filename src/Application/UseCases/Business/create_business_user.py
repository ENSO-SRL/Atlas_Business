import uuid
from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import EmailAlreadyInUseError
from src.Application.UseCases.Business.list_business_users import BusinessUserResult
from src.Domain.Entities.business_user import BusinessUser
from src.Domain.Entities.user import User
from src.Domain.Enums.system_role import SystemRole
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Repositories.i_user_repository import IUserRepository
from src.Domain.Ports.Services.i_password_hashing_service import IPasswordHashingService


@dataclass
class CreateBusinessUserCommand:
    business_id: UUID
    actor_id: UUID
    roles: list[str]
    email: str
    # Datos opcionales (requeridos si el usuario no existe)
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    plain_password: str | None = None


class CreateBusinessUserUseCase:
    """
    Agrega un usuario a un negocio.
    Si el usuario no existe globalmente, lo crea. Si ya existe, lo vincula.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        business_user_repo: IBusinessUserRepository,
        password_service: IPasswordHashingService,
    ):
        self.user_repo = user_repo
        self.business_user_repo = business_user_repo
        self.password_service = password_service

    async def execute(self, command: CreateBusinessUserCommand) -> BusinessUserResult:
        # 1. Buscar si el User ya existe globalmente
        user = await self.user_repo.get_by_email(command.email)

        if user:
            # 2a. Si existe, verificar que no esté ya vinculado al negocio
            existing_link = await self.business_user_repo.get_by_user_and_business(user.id, command.business_id)
            if existing_link:
                # TODO: Implementar excepción específica AlreadyMemberError
                raise ValueError("El usuario ya pertenece a este negocio.")
        else:
            # 2b. Si no existe, crear el nuevo User
            if not command.first_name or not command.last_name or not command.plain_password:
                raise ValueError("Se requieren first_name, last_name y plain_password para crear un usuario nuevo.")

            try:
                user_id = uuid.uuid7()
            except AttributeError:
                user_id = uuid.uuid4()

            hashed_password = self.password_service.hash(command.plain_password)

            user = User(
                id=user_id,
                first_name=command.first_name,
                last_name=command.last_name,
                email=command.email,
                phone=command.phone,
                hashed_password=hashed_password,
                is_active=True,
            )
            await self.user_repo.create(user)

        # 3. Vincular el User al Business
        roles = [SystemRole(r) for r in command.roles]

        try:
            link_id = uuid.uuid7()
        except AttributeError:
            link_id = uuid.uuid4()

        business_user = BusinessUser(
            id=link_id,
            user_id=user.id,
            business_id=command.business_id,
            roles=roles,
            is_active=True,
            created_by=command.actor_id,
        )

        await self.business_user_repo.create(business_user)

        return BusinessUserResult(
            id=business_user.id,
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            roles=[r.value for r in business_user.roles],
            is_active=business_user.is_active,
        )
