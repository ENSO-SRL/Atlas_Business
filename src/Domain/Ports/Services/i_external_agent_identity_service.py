from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.Domain.Enums.gender import Gender


@dataclass
class AgentUserIdentity:
    first_name: str
    last_name: str
    phone: str
    email: str | None
    gender: Gender | None


class IExternalAgentIdentityService(ABC):
    @abstractmethod
    async def get_user_info_by_phone(self, phone: str) -> AgentUserIdentity | None:
        """
        Consulta al servicio externo del Agente IA para obtener el perfil 
        asociado a un número de teléfono.
        Retorna None si no existe el usuario en ese ecosistema.
        """
        ...
