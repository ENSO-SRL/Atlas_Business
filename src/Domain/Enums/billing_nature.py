from enum import Enum


class BillingNature(str, Enum):
    BILLABLE = "BILLABLE"
    NON_BILLABLE = "NON_BILLABLE"
