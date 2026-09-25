import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import UUID

from src.Application.Exceptions.business_exceptions import CustomerNotFoundError, ServiceNotFoundError
from src.Application.Exceptions.client_exceptions import CustomFieldValidationError, InvalidPartySizeError, SlotNoLongerAvailableError
from src.Domain.Entities.booking import Booking
from src.Domain.Enums.billing_nature import BillingNature
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_business_customer_repository import IBusinessCustomerRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository
from src.Domain.Ports.Repositories.i_service_repository import IServiceRepository


@dataclass
class CreateInternalBookingCommand:
    business_id: UUID
    service_id: UUID
    customer_id: UUID
    actor_id: UUID
    date: date
    start_time: str  # "HH:MM"
    party_size: int
    bookable_object_id: UUID | None
    custom_fields: dict[str, Any]


@dataclass
class CreateBookingResult:
    id: UUID
    service_id: UUID
    bookable_object_id: UUID
    bookable_object_name: str | None
    start_time: str
    end_time: str
    party_size: int
    calculated_amount: str | None
    custom_fields: dict[str, Any]


class CreateInternalBookingUseCase:
    """
    Crea una reserva desde el dashboard del negocio (POS).
    Valida pertenencia de cliente y servicio al negocio, y registra la reserva
    a nombre del empleado (actor_id).
    """

    def __init__(
        self,
        service_repo: IServiceRepository,
        bookable_object_repo: IBookableObjectRepository,
        client_booking_repo: IClientBookingRepository,
        custom_field_repo: ICustomFieldRepository,
        rate_repo: IServiceRateRepository,
        customer_repo: IBusinessCustomerRepository,
    ):
        self.service_repo = service_repo
        self.bookable_object_repo = bookable_object_repo
        self.client_booking_repo = client_booking_repo
        self.custom_field_repo = custom_field_repo
        self.rate_repo = rate_repo
        self.customer_repo = customer_repo

    async def execute(self, command: CreateInternalBookingCommand) -> CreateBookingResult:
        if command.party_size < 1:
            raise InvalidPartySizeError()

        service = await self.service_repo.get_by_id(command.service_id, command.business_id)
        if not service:
            raise ServiceNotFoundError()

        customer = await self.customer_repo.get_by_id(command.customer_id, command.business_id)
        if not customer:
            raise CustomerNotFoundError()

        # 1. Validar campos personalizados
        custom_fields = await self.custom_field_repo.list_by_service(service.id)
        errors = []
        for cf in custom_fields:
            str_id = str(cf.id)
            value = command.custom_fields.get(str_id)
            success, msg = cf.validate_response(value)
            if not success:
                errors.append(msg)
                    
        if errors:
            raise CustomFieldValidationError(errors)

        slot_start = datetime.combine(command.date, time.fromisoformat(command.start_time)).replace(tzinfo=timezone.utc)
        slot_end = slot_start + timedelta(minutes=service.occupation_duration_minutes)
        booking_end = slot_start + timedelta(minutes=service.occupation_duration_minutes + service.buffer_minutes)

        # 2. Determinar el bookable_object_id
        assigned_object = None
        all_objects = await self.bookable_object_repo.list_by_service(service.id)
        
        if command.bookable_object_id:
            assigned_object = next((obj for obj in all_objects if obj.id == command.bookable_object_id), None)
            if not assigned_object or not assigned_object.is_active:
                raise SlotNoLongerAvailableError()
            if not (assigned_object.min_capacity <= command.party_size <= assigned_object.max_capacity):
                raise SlotNoLongerAvailableError()
                
            occupied_ids = await self.client_booking_repo.get_occupied_object_ids(
                [assigned_object.id], slot_start, booking_end
            )
            if assigned_object.id in occupied_ids:
                raise SlotNoLongerAvailableError()
        else:
            qualified_objects = [
                obj for obj in all_objects
                if obj.is_active and obj.min_capacity <= command.party_size <= obj.max_capacity
            ]
            if not qualified_objects:
                raise SlotNoLongerAvailableError()
                
            qualified_ids = [obj.id for obj in qualified_objects]
            occupied_ids = await self.client_booking_repo.get_occupied_object_ids(
                qualified_ids, slot_start, booking_end
            )
            
            available_objects = [obj for obj in qualified_objects if obj.id not in occupied_ids]
            if not available_objects:
                raise SlotNoLongerAvailableError()
                
            available_objects.sort(key=lambda x: x.max_capacity)
            assigned_object = available_objects[0]

        # 3. Calcular monto
        calculated_amount = None
        if service.billing_nature.value == BillingNature.BILLABLE.value:
            rates = await self.rate_repo.list_by_service(service.id)
            rate_info = self._find_rate(rates, slot_start, command.party_size)
            if rate_info:
                calculated_amount = rate_info

        # 4. Crear la reserva
        try:
            booking_id = uuid.uuid7()
        except AttributeError:
            booking_id = uuid.uuid4()

        booking = Booking(
            id=booking_id,
            service_id=service.id,
            bookable_object_id=assigned_object.id,
            start_time=slot_start,
            end_time=slot_end,
            party_size=command.party_size,
            customer_id=customer.id,
            calculated_amount=calculated_amount,
            custom_fields=command.custom_fields,
            created_by=command.actor_id,
        )

        await self.client_booking_repo.create(booking)

        return CreateBookingResult(
            id=booking.id,
            service_id=booking.service_id,
            bookable_object_id=booking.bookable_object_id,
            bookable_object_name=assigned_object.name,
            start_time=booking.start_time.isoformat(),
            end_time=booking.end_time.isoformat(),
            party_size=booking.party_size,
            calculated_amount=str(booking.calculated_amount) if booking.calculated_amount is not None else None,
            custom_fields=booking.custom_fields,
        )

    def _find_rate(self, rates: list, slot_start: datetime, party_size: int) -> float | None:
        weekday_name = slot_start.strftime("%A").upper()
        slot_time = slot_start.time()

        for rate in rates:
            if weekday_name in rate.weekdays:
                if rate.start_time <= slot_time < rate.end_time:
                    base = rate.amount
                    total = base * party_size if rate.calculation_basis.value == CalculationBasis.PER_PERSON.value else base
                    return float(total)
        return None
