from src.Domain.Enums.gender import Gender
from src.Domain.Ports.Services.i_external_agent_identity_service import (
    AgentUserIdentity,
    IExternalAgentIdentityService,
)


class DummyExternalAgentIdentityService(IExternalAgentIdentityService):
    """
    Implementación simulada que retorna usuarios generados proceduralmente para pruebas locales
    mientras no haya conexión real al sistema del Agente IA.
    """
    
    async def get_user_info_by_phone(self, phone: str) -> AgentUserIdentity | None:
        # Simulamos que algunos prefijos son de usuarios que no existen.
        if phone.startswith("000"):
            return None
            
        return AgentUserIdentity(
            first_name="Usuario",
            last_name=f"Demo {phone[-4:]}",
            phone=phone,
            email=f"demo_{phone[-4:]}@example.com",
            gender=Gender.MALE if int(phone[-1]) % 2 == 0 else Gender.FEMALE
        )
