from enum import Enum

class SystemRole(Enum):
    """
    Roles del sistema para los usuarios de negocio (BusinessUser).
    """
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    RECEPTIONIST = "RECEPTIONIST"
