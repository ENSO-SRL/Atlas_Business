import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.Application.Exceptions.client_exceptions import CustomFieldValidationError, InvalidPartySizeError, ServiceNotPublicError, SlotNoLongerAvailableError
from src.Domain.Entities.booking import Booking
from src.Domain.Enums.billing_nature import BillingNature
from src.Domain.Enums.calculation_basis import CalculationBasis
from src.Domain.Ports.Repositories.i_bookable_object_repository import IBookableObjectRepository
from src.Domain.Ports.Repositories.i_client_booking_repository import IClientBookingRepository
from src.Domain.Ports.Repositories.i_client_service_repository import IClientServiceRepository
from src.Domain.Ports.Repositories.i_custom_field_repository import ICustomFieldRepository
from src.Domain.Ports.Repositories.i_service_rate_repository import IServiceRateRepository


@dataclass
class CreateBookingCommand:
    service_id: UUID
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


class CreateBookingUseCase:
    """
    Crea una reserva, validando campos personalizados y asignando el objeto de forma manual o automática.
    """

    def __init__(
        self,
        client_service_repo: IClientServiceRepository,
        bookable_object_repo: IBookableObjectRepository,
        client_booking_repo: IClientBookingRepository,
        custom_field_repo: ICustomFieldRepository,
        rate_repo: IServiceRateRepository,
    ):
        self.client_service_repo = client_service_repo
        self.bookable_object_repo = bookable_object_repo
        self.client_booking_repo = client_booking_repo
        self.custom_field_repo = custom_field_repo
        self.rate_repo = rate_repo

    async def execute(self, command: CreateBookingCommand) -> CreateBookingResult:
        if command.party_size < 1:
            raise InvalidPartySizeError()

        service = await self.client_service_repo.get_published_by_id_only(command.service_id)
        if not service:
            raise ServiceNotPublicError()

        # 1. Validar campos personalizados
        custom_fields = await self.custom_field_repo.list_by_service(service.id)
        errors = []
        for cf in custom_fields:
            # Solo los visibles al cliente deberían ser enviados, pero validamos todos por seguridad
            if cf.visible_to_client:
                # El cliente envía dict con claves como strings
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
                
            # Verificar si está ocupado
            occupied_ids = await self.client_booking_repo.get_occupied_object_ids(
                [assigned_object.id], slot_start, booking_end
            )
            if assigned_object.id in occupied_ids:
                raise SlotNoLongerAvailableError()
        else:
            # Asignación automática
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
                
            # CLOSEST_MAX_CAPACITY
            available_objects.sort(key=lambda x: x.max_capacity)
            assigned_object = available_objects[0]

        # 3. Calcular monto
        calculated_amount = None
        if service.billing_nature == BillingNature.BILLABLE:
            rates = await self.rate_repo.list_by_service(service.id)
            rate_info = self._find_rate(rates, slot_start, command.party_size)
            if rate_info:
                calculated_amount = rate_info

        # 4. Crear reserva
        try:
            booking_id = uuid.uuid7()
        except AttributeError:
            booking_id = uuid.uuid4()
            
        booking = Booking(
            id=booking_id,
            business_id=service.business_id,
            service_id=service.id,
            bookable_object_id=assigned_object.id,
            start_time=slot_start,
            end_time=booking_end, # end_time de la reserva incluye el buffer
            party_size=command.party_size,
            calculated_amount=calculated_amount,
            custom_fields=command.custom_fields,
            agent_notes=None,
        )

        # Aquí si hay una violación de Exclusión GiST (race condition), 
        # el repositorio debería levantar la excepción subyacente que 
        # el Controller mapeará a SlotNoLongerAvailableError
        await self.client_booking_repo.create(booking)

        return CreateBookingResult(
            id=booking.id,
            service_id=service.id,
            bookable_object_id=assigned_object.id,
            bookable_object_name=assigned_object.name,
            start_time=slot_start.isoformat(),
            end_time=slot_end.isoformat(), # Al cliente se le muestra sin el buffer
            party_size=command.party_size,
            calculated_amount=f"{calculated_amount:.2f}" if calculated_amount is not None else None,
            custom_fields=command.custom_fields,
        )

    def _find_rate(self, rates: list, slot_start: datetime, party_size: int) -> Decimal | None:
        weekday_name = slot_start.strftime("%A").upper()
        slot_time = slot_start.time()

        for rate in rates:
            if weekday_name in rate.weekdays:
                if rate.start_time <= slot_time < rate.end_time:
                    base = rate.amount
                    return base * party_size if rate.calculation_basis == CalculationBasis.PER_PERSON else base
        return None
