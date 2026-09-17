from enum import Enum


class CalculationBasis(str, Enum):
    PER_BOOKING = "PER_BOOKING"
    PER_PERSON = "PER_PERSON"
