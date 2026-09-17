from enum import Enum


class DurationNature(str, Enum):
    FIXED = "FIXED"
    ESTIMATED = "ESTIMATED"
    INSTANT = "INSTANT"
