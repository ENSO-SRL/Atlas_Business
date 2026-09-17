from enum import Enum

class SystemRole(Enum):
    """
    Roles del sistema para los usuarios de negocio (BusinessUser).
    """
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"
