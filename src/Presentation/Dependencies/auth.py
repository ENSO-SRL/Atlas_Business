from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt

from src.Settings.settings import Settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/business/auth/token")
CLIENT_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)


@dataclass
class UserContext:
    user_id: UUID
    business_id: UUID | None  # Puede ser None si el JWT aún no tiene contexto de negocio
    roles: list[str]


def get_settings() -> Settings:
    return Settings()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> UserContext:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        business_id_str = payload.get("business_id")
        return UserContext(
            user_id=UUID(payload["sub"]),
            business_id=UUID(business_id_str) if business_id_str else None,
            roles=payload.get("roles", []),
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")


def require_business_context(user: UserContext = Depends(get_current_user)) -> UserContext:
    """Asegura que el JWT contenga un business_id válido."""
    if not user.business_id:
        raise HTTPException(status_code=403, detail="Se requiere haber seleccionado un negocio.")
    return user


def require_admin(user: UserContext = Depends(require_business_context)) -> UserContext:
    """Guard para endpoints solo-ADMIN u OWNER."""
    if "ADMIN" not in user.roles and "OWNER" not in user.roles:
        raise HTTPException(status_code=403, detail="Se requiere rol ADMIN u OWNER.")
    return user


async def require_api_key(
    api_key: str = Security(CLIENT_API_KEY_HEADER),
    settings: Settings = Depends(get_settings),
) -> None:
    """Validación de API Key para Client API."""
    if api_key != settings.CLIENT_API_KEY:
        raise HTTPException(status_code=403, detail="API Key inválida.")
