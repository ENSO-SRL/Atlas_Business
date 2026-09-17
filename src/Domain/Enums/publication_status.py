from enum import Enum

class PublicationStatus(Enum):
    """
    Estado de publicación de un Service.
    """
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REJECTED = "REJECTED"
