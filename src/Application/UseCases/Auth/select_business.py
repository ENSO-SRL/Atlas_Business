from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ApplicationError
from src.Domain.Ports.Repositories.i_business_user_repository import IBusinessUserRepository
from src.Domain.Ports.Services.i_token_service import ITokenService


@dataclass
class SelectBusinessCommand:
    user_id: UUID
    business_id: UUID


@dataclass
class SelectBusinessResult:
    access_token: str


class BusinessAccessDeniedError(ApplicationError):
    def __init__(self):
        super().__init__("No tienes acceso a este negocio o está inactivo.")


class SelectBusinessUseCase:
    def __init__(
        self,
        business_user_repo: IBusinessUserRepository,
        token_service: ITokenService,
    ):
        self._business_user_repo = business_user_repo
        self._token_service = token_service

    async def execute(self, command: SelectBusinessCommand) -> SelectBusinessResult:
        business_user = await self._business_user_repo.get_by_user_and_business(
            user_id=command.user_id, business_id=command.business_id
        )

        if not business_user or not business_user.is_active:
            raise BusinessAccessDeniedError()

        # Generar nuevo access_token con contexto de negocio
        access_token = self._token_service.create_access_token(
            user_id=command.user_id,
            business_id=command.business_id,
            roles=[role.value for role in business_user.roles]
        )

        return SelectBusinessResult(access_token=access_token)
