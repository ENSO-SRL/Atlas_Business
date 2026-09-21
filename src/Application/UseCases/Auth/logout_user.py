from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.Application.Exceptions.business_exceptions import ApplicationError
from src.Domain.Ports.Repositories.i_token_blacklist_repository import ITokenBlacklistRepository
from src.Domain.Ports.Services.i_token_service import ITokenService


@dataclass
class LogoutUserCommand:
    refresh_token: str


class LogoutUserUseCase:
    def __init__(
        self,
        token_blacklist_repo: ITokenBlacklistRepository,
        token_service: ITokenService,
    ):
        self._token_blacklist_repo = token_blacklist_repo
        self._token_service = token_service

    async def execute(self, command: LogoutUserCommand) -> None:
        try:
            payload = self._token_service.decode_token(command.refresh_token)
            
            jti_str = payload.get("jti")
            sub_str = payload.get("sub")
            exp = payload.get("exp")
            
            if not jti_str or not sub_str or not exp:
                return  # Si falta data, ignoramos y dejamos que se borren las cookies nomás

            jti = UUID(jti_str)
            user_id = UUID(sub_str)
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            
            # Guardamos en blacklist
            await self._token_blacklist_repo.revoke(jti, user_id, expires_at)
            
        except Exception:
            # Si el token ya expiró o es inválido, no podemos añadir a blacklist
            # de todos modos, así que fallamos silenciosamente, el objetivo de logout es
            # borrar cookies y en caso de que aún sirva el token, revocarlo.
            pass
