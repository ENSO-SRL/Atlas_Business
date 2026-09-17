from enum import Enum


class ContentRequestStatus(str, Enum):
    PENDING_FILTER = "PENDING_FILTER"
    APPROVED = "APPROVED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
