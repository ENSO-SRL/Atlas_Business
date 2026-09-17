from enum import Enum

class VerificationStatus(Enum):
    """
    Estados del flujo de verificación de un Business.
    """
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"
