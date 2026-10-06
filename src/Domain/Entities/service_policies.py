from dataclasses import dataclass
from enum import Enum


class PaymentStage(Enum):
    PRE_BOOKING = "PRE_BOOKING"
    RECEPTION = "RECEPTION"
    CHECKOUT = "CHECKOUT"


class PaymentMethod(Enum):
    TRANSFER = "TRANSFER"
    CARD = "CARD"
    CASH = "CASH"


@dataclass
class PaymentSplit:
    stage: PaymentStage
    percentage: float  # 0.0 a 100.0
    allowed_methods: list[PaymentMethod]


@dataclass
class PaymentAndCancellationPolicy:
    payment_splits: list[PaymentSplit]
    cancellation_description: str | None
    min_cancellation_margin_hours: int | None
    cancellation_fee: float | None


@dataclass
class ModificationPolicy:
    allows_same_day_reschedule: bool | None
    allows_date_change: bool | None
    date_change_margin_days: int | None


@dataclass
class ArrivalAndConfirmationPolicy:
    wait_time_minutes: int | None
    release_automatically: bool | None
