from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from src.Application.Exceptions.business_exceptions import ApplicationError
from src.Domain.Ports.Services.i_token_service import ITokenService
from src.Settings.settings import Settings


class InvalidTokenError(ApplicationError):
    def __init__(self, message="Token inválido o expirado"):
        super().__init__(message)


class JwtTokenService(ITokenService):
    def __init__(self, settings: Settings):
        self._settings = settings

    def create_access_token(self, user_id: UUID, business_id: UUID | None = None, roles: list[str] | None = None, is_superadmin: bool = False) -> str:
        expires_delta = timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "is_superadmin": is_superadmin,
        }
        
        if business_id is not None:
            to_encode["business_id"] = str(business_id)
        if roles is not None:
            to_encode["roles"] = roles
            
        return jwt.encode(to_encode, self._settings.SECRET_KEY, algorithm=self._settings.ALGORITHM)

    def create_refresh_token(self, user_id: UUID, jti: UUID) -> str:
        expires_delta = timedelta(days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "jti": str(jti),
            "exp": expire,
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self._settings.SECRET_KEY, algorithm=self._settings.ALGORITHM)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self._settings.SECRET_KEY, algorithms=[self._settings.ALGORITHM])
            return payload
        except JWTError:
            raise InvalidTokenError()
