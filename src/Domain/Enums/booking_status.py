from enum import Enum

class BookingStatus(Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
