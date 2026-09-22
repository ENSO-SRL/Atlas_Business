from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID, business_id: UUID | None = None, roles: list[str] | None = None, is_superadmin: bool = False) -> str:
        """Genera un JWT de acceso de corta duración."""
        pass

    @abstractmethod
    def create_refresh_token(self, user_id: UUID, jti: UUID) -> str:
        """Genera un JWT de refresco de larga duración con un JWT ID (jti) único."""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        """Verifica y decodifica el token. Levanta excepción si es inválido o expiró."""
        pass
