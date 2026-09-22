from dataclasses import dataclass
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ApplicationError
from src.Domain.Ports.Repositories.i_token_blacklist_repository import ITokenBlacklistRepository
from src.Domain.Ports.Services.i_token_service import ITokenService


@dataclass
class RefreshAccessTokenCommand:
    refresh_token: str
    current_business_id: UUID | None = None
    current_roles: list[str] | None = None
    is_superadmin: bool = False


@dataclass
class RefreshAccessTokenResult:
    access_token: str


class InvalidRefreshTokenError(ApplicationError):
    def __init__(self):
        super().__init__("Refresh token inválido, expirado o revocado.")


class RefreshAccessTokenUseCase:
    def __init__(
        self,
        token_blacklist_repo: ITokenBlacklistRepository,
        token_service: ITokenService,
    ):
        self._token_blacklist_repo = token_blacklist_repo
        self._token_service = token_service

    async def execute(self, command: RefreshAccessTokenCommand) -> RefreshAccessTokenResult:
        try:
            payload = self._token_service.decode_token(command.refresh_token)
        except Exception:
            raise InvalidRefreshTokenError()

        # Validar que sea un refresh token
        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenError()

        jti_str = payload.get("jti")
        sub_str = payload.get("sub")

        if not jti_str or not sub_str:
            raise InvalidRefreshTokenError()

        jti = UUID(jti_str)
        user_id = UUID(sub_str)

        # Validar blacklist
        is_revoked = await self._token_blacklist_repo.is_revoked(jti)
        if is_revoked:
            raise InvalidRefreshTokenError()

        # Emitir nuevo access token conservando el contexto si lo tenía
        access_token = self._token_service.create_access_token(
            user_id=user_id,
            business_id=command.current_business_id,
            roles=command.current_roles,
            is_superadmin=command.is_superadmin,
        )

        return RefreshAccessTokenResult(access_token=access_token)
